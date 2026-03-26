# CLAUDE.md — Skarnik Admin

AI agent guide for working in this repository.

## Project Overview

**Skarnik Admin** is a Django backend for administering the [Skarnik](https://skarnik.by) Belarusian dictionary. It manages word entries, HTML-formatted translations, stress marks (accent positions), and search indexing. The admin UI is the primary interface; a small read-only REST API serves the frontend.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Framework | Django 5.2 + Django REST Framework 3.16.1 |
| Database | MySQL/MariaDB (production), SQLite (dev/test) |
| Search | Typesense 0.21.0 |
| Rich text editor | TinyMCE 5 (via django-tinymce 5.0.0) |
| HTML parsing | BeautifulSoup4 + lxml |
| Version history | django-reversion 6.1.0 |
| App server | uWSGI (production) |
| Dev extras | django-extensions, django-debug-toolbar |

## Architecture

```
skarnik_admin/
├── config/
│   ├── settings/
│   │   ├── base.py          # Core settings (DB, logging, installed apps)
│   │   ├── development.py   # Debug toolbar, relaxed hosts
│   │   ├── testing.py       # In-memory SQLite
│   │   └── production.py    # DEBUG=False, restricted hosts
│   ├── urls.py              # Root routing: /admin/, /api/, /tinymce/
│   ├── asgi.py
│   └── wsgi.py
├── main/                    # Single Django app
│   ├── models.py            # Word (managed) + Translation (unmanaged, legacy table)
│   ├── serializers.py       # WordSerializer (all fields)
│   ├── views.py             # 2 read-only API views
│   ├── urls.py              # /api/words/<pk>/ and /api/words/<direction>/<external_id>/
│   ├── admin.py             # WordAdmin + TranslationAdmin (VersionAdmin)
│   ├── admin_filters.py     # LetterListFilter + DirectionListFilter
│   ├── migrations/
│   └── management/commands/ # 11 data-processing commands (see below)
│       └── tests/
│           ├── test_models.py
│           ├── test_views.py
│           └── test_serializers.py
├── requirements/
│   ├── base.txt
│   ├── development.txt      # + debug-toolbar
│   └── production.txt       # + uWSGI
└── logs/                    # Rotating logs: debug.log, db.log
```

## Data Model

### `Word` (main table, managed)
| Field | Type | Notes |
|-------|------|-------|
| `id` | AutoField PK | |
| `external_id` | IntegerField | ID on legacy skarnik.by |
| `direction` | CharField | `be-ru`, `ru-be`, `tsbm` |
| `letter` | CharField | First letter (for browsing) |
| `text` | CharField | The word itself |
| `translation` | HTMLField | Rich HTML from TinyMCE |
| `redirect_to` | URLField | Optional redirect URL |
| `stress` | CharField | Stress marks (optional) |

Unique constraint: `(external_id, direction)`.

### `Translation` (unmanaged, legacy `translations` table)
Same shape as `Word`; used as read-only source for data migration. Has `.to_word()` method.

## API Endpoints

```
GET /api/words/<int:pk>/
GET /api/words/<str:direction>/<int:external_id>/
```

Both return `WordSerializer` JSON. Both are read-only (no auth required currently).

## Dictionary Directions

| Code | Meaning |
|------|---------|
| `be-ru` | Belarusian → Russian |
| `ru-be` | Russian → Belarusian |
| `tsbm` | ТСБМ (Тлумачальны слоўнік беларускай мовы) — explanatory dictionary |

## Management Commands

Run with: `python manage.py <command> [options]`

| Command | Purpose |
|---------|---------|
| `fill_stress` | Fetch stress marks from starnik.by API (TSBM) |
| `fill_stress_bnk` | Fetch stress marks from bnkorpus.info API; supports `--direction`, `--dry-run`, `--print-words`, `--limit` |
| `sync_typesense` | Rebuild Typesense `words` collection (batch 1000) |
| `check_typesense` | Print Typesense collection metadata |
| `copy_translations_to_words` | Bulk-copy legacy `Translation` rows → `Word` table |
| `fill_redirect_to` | Extract redirect URLs from `<a>` tags in translation HTML |
| `remove_nbsps` | Replace raw `&nbsp;` with `<span>&nbsp;</span>` across translations |
| `fix_colors` | Fix/normalise color attributes in HTML |
| `find_inner_stress` | Find colored/linked elements, enrich with `data-word`/`data-link` attributes |
| `fix_inner_stress` | Split comma-separated word lists in HTML, wrap each with stress data-attrs |

## Common Dev Commands

```bash
# Activate virtual environment
source ENV/bin/activate

# Run development server
python manage.py runserver --settings=config.settings.development

# Run tests
python manage.py test main --settings=config.settings.testing

# Django shell (with auto-imports via django-extensions)
python manage.py shell_plus --settings=config.settings.development

# Migrations
python manage.py makemigrations
python manage.py migrate

# Sync search index
python manage.py sync_typesense

# Fetch stress marks for be-ru direction
python manage.py fill_stress_bnk --direction be-ru
```

## Settings & Secrets

Settings module is selected via `DJANGO_SETTINGS_MODULE` environment variable (set in `.envrc`).

Secrets (DB credentials, Typesense API key, etc.) are loaded from `secrets.json` at project root — never commit this file.

## Logging

Configured in `config/settings/base.py`:
- `logs/debug.log` — general application log
- `logs/db.log` — SQL queries; rotates through 10 backup files
- Slow queries (>0.3s) are flagged in the DB log

## Testing

- Uses `config.settings.testing` (in-memory SQLite, no migrations needed via `--keepdb`)
- Test files in `main/tests/`
- Framework: `django.test.TestCase` + `rest_framework.test.APITestCase`

```bash
python manage.py test main --settings=config.settings.testing
```

## Code Conventions

- **Language in UI/models:** Belarusian (`verbose_name` fields use Belarusian strings)
- **HTML content:** Always stored and edited via TinyMCE; parse with BeautifulSoup4
- **Admin views:** Extend `VersionAdmin` (django-reversion) for change tracking
- **Management commands:** Add `--dry-run` option for any destructive/bulk operation
- **Batch DB writes:** Use `bulk_create`/`bulk_update` with `batch_size=1000`

## Key Integration Points

- **Typesense:** Collection name is `words`; schema mirrors `Word.to_typesense()` output; `be-BY` locale on text fields
- **starnik.by / bnkorpus.info:** External APIs used only in management commands; HTTP via `requests`
- **Legacy DB:** The `translations` table is read-only via the unmanaged `Translation` model; do not write to it
