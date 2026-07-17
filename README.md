# Skarnik Admin

Django administration backend for the [Skarnik](https://skarnik.by) Belarusian dictionary.

## What It Does

- Manages word entries with HTML-formatted translations across three dictionary directions (Belarusian→Russian, Russian→Belarusian, explanatory ТСБМ)
- Tracks stress marks (accent positions) on words, enriched via external APIs and a Supabase-sourced `StressWord` table
- Provides a read-only REST API consumed by the skarnik.by frontend
- Syncs the word index to Typesense for full-text search

## Stack

- **Python 3.13** / **Django 5.2** / **Django REST Framework 3.16.1**
- **MySQL/MariaDB** (production) — SQLite for development/testing
- **Typesense** for full-text search
- **TinyMCE** for rich-text translation editing
- **django-reversion** for change history in the admin
- **Supabase** as source for `StressWord` import/sync

## Quick Start

```bash
# Clone and set up virtual environment
python -m venv ENV
source ENV/bin/activate
pip install -r requirements/development.txt

# Configure secrets — create secrets.json at project root with:
# SECRET_KEY, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST,
# TYPESENSE_KEY, SUPABASE_URL, SUPABASE_KEY

# Apply migrations
python manage.py migrate --settings=config.settings

# Run development server (MODE defaults to development, so it can be omitted)
python manage.py runserver --settings=config.settings
```

## Running Tests

```bash
MODE=testing python manage.py test main --settings=config.settings
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/words/<id>/` | Word by primary key |
| `GET /api/words/<direction>/<external_id>/` | Word by direction + external ID |
| `GET /api/stress_words/?word=<text>` | StressWord entries matching a word (lowercased) |
| `GET /api/stress_words/<id>/` | StressWord by primary key |

Directions: `be-ru`, `ru-be`, `tsbm`

## Management Commands

```bash
# Sync Typesense search index
python manage.py sync_typesense

# Fetch stress marks from external API
python manage.py fill_stress_bnk --direction be-ru [--dry-run] [--limit N]

# Copy legacy translations table to words table
python manage.py copy_translations_to_words

# Import StressWord rows from Supabase
python manage.py import_stress_words_from_supabase [--page-size N] [--limit N] [--dry-run]
```

See `CLAUDE.md` for the full command reference and developer guide.

## Project Structure

```
config/          Django settings (base / development / testing / production)
main/            Single app: models, views, serializers, admin, management commands
requirements/    Layered requirements files (base / development / production)
logs/            Rotating application and DB query logs
```

## Settings

Always pass `--settings=config.settings` (the package, not a submodule) and select the mode via the `MODE` env var:

| `MODE` | Use |
|--------|-----|
| _(unset)_ / `development` | Local development |
| `testing` | Test runs (in-memory SQLite) |
| `production` | Production server |

Pointing `--settings` directly at `config.settings.development`/`.testing`/`.production` re-imports that submodule standalone before `base.py` finishes loading, and crashes with `NameError: name 'INSTALLED_APPS' is not defined`.
