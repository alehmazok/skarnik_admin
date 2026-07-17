# Add StressWord model + Supabase import (handoff doc for a fresh Claude Code session)

This doc is self-contained context for implementing this in `skarnik_admin`. It was planned in a separate Claude Code session working on the `skarnik_flutter` repo, which has no access to this repo — so everything relevant is inlined below rather than referenced.

## Background

`skarnik_flutter` (the mobile app) added a word-stress/declension-table lookup feature backed by GrammarDB (https://github.com/Belarus/GrammarDB) data, stored in this project's Supabase instance as a `stress_word` table (~248k rows, ~486MB). That pushed Supabase's total DB size to 676MB, over the free tier's 500MB cap.

This backend (`skarnik_admin`, Django + MariaDB 10.5.27, serves `skarnik.by`) has real disk and already has Supabase sync precedent (`main/supabase_sync.py`, syncs the `main_word` table). Plan: pull the already-computed `stress_word` data out of Supabase into a new local `StressWord` model here, expose it over the existing API convention, and (once the Flutter app is switched over and verified) the Supabase `stress_word` table gets dropped to reclaim the space. **This doc covers only the Django side** — the Flutter-side repository swap is a separate change in `skarnik_flutter`, but the API contract below is what it will call, so don't deviate from the shapes without checking back.

## Source data shape (Supabase `stress_word` table, what you're pulling FROM)

```
id              bigint, PK
word            varchar   -- unstressed headword, ALWAYS lowercase (search key)
lemma           varchar   -- stressed display form, combining acute U+0301 encoded
table_name      varchar, nullable   -- POS label, one of: Nouns, Adjectives, Verbs,
                                       Participles, Pronouns, Numerals, Adverbs,
                                       Conjunctions, Prepositions, Particles,
                                       Interjections, or null
source_pdg_id   bigint, nullable, unique   -- GrammarDB Paradigm pdgId, the idempotency key
rows            jsonb     -- [{"title": "<html>", "content": "<html>"}, ...] precomputed
                             declension/conjugation table, e.g.:
                             [{"title": "Назоўны<br><span class=\"pytanne\">хто? што?</span>",
                               "content": "<b> рука́ </b><br><br><span class=\"skarot\">мн.</span>&nbsp;<b> ру́кі </b>"}]
```

Two data-quality bugs were found and fixed in the Supabase copy during that work (worth knowing since they inform what the test fixture should cover):
1. `word` wasn't always lowercase originally (proper nouns) — fixed, now always lowercase in the source. Import as-is (already normalized).
2. A parsing bug briefly dropped some valid homonym rows (e.g. the `пара` trio: `па́ра` "pair" pdgId 1021373, `па́ра` "steam" pdgId 1021374, `пара́` general pdgId 1179072 — three distinct rows, same `word`, different `lemma`/`source_pdg_id`) — already fixed and re-imported in Supabase, but it's a good real-world regression case: a single `word` value legitimately maps to multiple rows (homonyms), and casing must stay lowercase.

## Existing conventions in this repo (already confirmed, so you don't need to re-derive them)

- Single app `main`. Models in `main/models.py`, serializers in `main/serializers.py`, views in `main/views.py`, urls in `main/urls.py` mounted under `/api/` (`config/urls.py`).
- Existing `Word` model/`WordSerializer`/`WordByIdRetrieveAPIView`/`WordByExternalIdRetrieveAPIView` (`main/urls.py:6-15`) is the pattern to mirror — DRF `generics.RetrieveAPIView`/`ListAPIView`, not viewsets.
- DB: MariaDB via `django.db.backends.mysql`, credentials from `secrets.json` (not env vars) via `get_secret()` in `config/settings/base.py`.
- `main/supabase_sync.py` already has `_client()` returning `create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)` — reuse this, don't duplicate. `settings.SUPABASE_URL`/`SUPABASE_KEY` already exist in `secrets.json`, no new secrets needed.
- Management commands live in `main/management/commands/`. Bulk-write convention: `bulk_create(chunk, batch_size=...)` in a loop (see `copy_translations_to_words.py`, `chunk_size = 500`). `CLAUDE.md` in this repo states the convention explicitly: batch DB writes with `batch_size=1000`, and add `--dry-run` for destructive/bulk commands.
- Testing: **no pytest** — plain `django.test.TestCase` / `rest_framework.test.APITestCase`, inline `Model.objects.create(...)` in `setUp()`, no Django fixtures (`loaddata`-style) used anywhere in the codebase currently. Tests live in `main/tests/` as a package (`test_models.py`, `test_serializers.py`, `test_views.py`), not `main/tests.py`. No existing mocking precedent (no `unittest.mock` usage yet anywhere in this repo) — you'll be introducing the first one, for the Supabase-pulling management command.
- No CI config exists in this repo (no GitHub Actions etc.) — tests are run manually via `manage.py test`.
- Two unrelated existing commands, `fill_stress.py`/`fill_stress_bnk.py`, already touch a `Word.stress` field (single accented-headword string for the existing translation feature, e.g. "сло́ва") — **not the same thing** as this declension-table data. No overlap, just don't confuse the two or collide on naming.

## What to build

### 1. Model — `main/models.py`

```python
class StressWord(models.Model):
    word = models.CharField(max_length=127, db_index=True, help_text="Слова без націску (ключ пошуку)")
    lemma = models.CharField(max_length=127, help_text="Слова з націскам")
    table_name = models.CharField(max_length=31, null=True, blank=True, help_text="Частка мовы")
    source_pdg_id = models.BigIntegerField(unique=True, null=True, blank=True, help_text="ID парадыгмы ў GrammarDB")
    rows = models.JSONField(help_text="Радкі табліцы скланення/спражэння")

    class Meta:
        verbose_name = "Слова з націскам"
        verbose_name_plural = "Словы з націскам"

    def __str__(self):
        return self.lemma
```

`word` must be stored lowercase (matches the source). MariaDB JSONField needs >=10.2.7; this server is 10.5.27, fine. Run `python manage.py makemigrations main` (continues the existing `0001_initial`/`0002_alter_word_text` numbering).

### 2. Serializers — `main/serializers.py`

Two, matching the two API endpoints below (list endpoint deliberately excludes the heavy `rows` field):

```python
class StressWordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StressWord
        fields = ["id", "word", "lemma", "table_name"]

class StressWordDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StressWord
        fields = ["id", "rows"]
```

### 3. Views — `main/views.py`

```python
class StressWordListAPIView(generics.ListAPIView):
    serializer_class = StressWordListSerializer

    def get_queryset(self):
        word = self.request.query_params.get('word', '')
        return StressWord.objects.filter(word=word.lower())


class StressWordRetrieveAPIView(generics.RetrieveAPIView):
    queryset = StressWord.objects.all()
    serializer_class = StressWordDetailSerializer
```

### 4. URLs — `main/urls.py`

```python
path('stress_words/', StressWordListAPIView.as_view(), name='stress_word_list'),
path('stress_words/<int:pk>/', StressWordRetrieveAPIView.as_view(), name='stress_word_detail'),
```

**API contract the Flutter app will call** (don't change without coordinating):
- `GET /api/stress_words/?word=<lowercase word>` → `[{"id": ..., "word": ..., "lemma": ..., "table_name": ...}, ...]` (0 or more; homonyms return multiple rows with the same `word`)
- `GET /api/stress_words/<id>/` → `{"id": ..., "rows": [{"title": "...", "content": "..."}, ...]}`

### 5. Management command — `main/management/commands/import_stress_words_from_supabase.py`

Pulls from the Supabase `stress_word` table (source shape above) into the new local model — NOT re-deriving from GrammarDB XML, that data is already correct in Supabase.

- Reuse `main.supabase_sync._client()`.
- Paginate: `.table('stress_word').select('id,word,lemma,table_name,source_pdg_id,rows').order('id').range(start, start + page_size - 1).execute()`, `page_size` default 1000, loop until an empty page comes back.
- Upsert via `StressWord.objects.bulk_create(chunk, batch_size=1000, update_conflicts=True, unique_fields=['source_pdg_id'], update_fields=['word', 'lemma', 'table_name', 'rows'])` — Django 5.2 on MariaDB compiles this to `INSERT ... ON DUPLICATE KEY UPDATE`, safe to re-run.
- `--dry-run` flag (fetch + report counts, write nothing) per this repo's stated convention for bulk/destructive commands.
- `--limit` flag, useful for smoke-testing against prod without pulling all 248k rows.
- Progress output per chunk via `self.stdout.write`.

### 6. Tests

Follow this repo's existing plain-`TestCase` style exactly, no pytest, no new test dependencies beyond stdlib `unittest.mock` (first use of mocking in this repo — needed here since the command talks to an external service).

- `main/tests/test_stress_word_model.py` — creation, `__str__`, `source_pdg_id` uniqueness (`assertRaises(IntegrityError)` on duplicate), `verbose_name`.
- `main/tests/test_stress_word_serializers.py` — list serializer excludes `rows`; detail serializer excludes `word`/`lemma`/`table_name`.
- `main/tests/test_stress_word_views.py` — `APITestCase`, mirror `test_views.py`'s structure: list-by-word (found, not-found, and a case-insensitivity check — query with mixed case, confirm it still matches because storage is lowercase), retrieve-by-pk (found, 404), and a homonyms case (two rows sharing `word`, both returned by the list endpoint).
- `main/tests/test_import_stress_words_from_supabase.py` — mock the Supabase client (`unittest.mock.patch` on wherever the command sources `_client`, e.g. `main.supabase_sync._client` or a local import of it) to return paged results built from the fixture below, terminated by an empty final page. Cover: normal run populates `StressWord` matching the fixture; `--dry-run` writes nothing; running twice updates existing rows via `source_pdg_id` rather than duplicating (the upsert path); `--limit` truncates correctly.

**Fixture** — `main/tests/fixtures/stress_word_supabase_sample.json`: a small hand-picked JSON array (3-4 rows) shaped exactly like the real Supabase rows (`id`, `word`, `lemma`, `table_name`, `source_pdg_id`, `rows` — see shape above). This is *not* a Django `loaddata` fixture (nothing seeds the DB directly with it) — it's the mocked Supabase response body the test patches in. Include the `пара` homonym trio described above (`source_pdg_id` 1021373 "pair", 1021374 "steam", 1179072 general — all `word="пара"`, different `lemma`) as real regression coverage: if the import logic or model ever mishandles homonyms or casing again, this fixture catches it immediately.

## Verification

1. `python manage.py test main.tests.test_stress_word_model main.tests.test_stress_word_serializers main.tests.test_stress_word_views main.tests.test_import_stress_words_from_supabase`
2. `python manage.py import_stress_words_from_supabase --dry-run` against real Supabase first (counts only), then for real.
3. Spot-check via `manage.py shell` or Django admin that the `пара` trio imported as 3 distinct rows, all lowercase `word`.
4. `curl` the two new endpoints directly (e.g. `curl https://skarnik.by/api/stress_words/?word=рука`, `curl https://skarnik.by/api/stress_words/<id>/`) before telling the Flutter side it's ready to switch over.

Do not drop anything in Supabase from this repo/session — that cleanup happens from the `skarnik_flutter` side once the Flutter app is verified working against these new endpoints.
