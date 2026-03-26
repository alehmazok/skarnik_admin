# Skarnik Admin

Django administration backend for the [Skarnik](https://skarnik.by) Belarusian dictionary.

## What It Does

- Manages word entries with HTML-formatted translations across three dictionary directions (Belarusian→Russian, Russian→Belarusian, explanatory ТСБМ)
- Tracks stress marks (accent positions) on words, enriched via external APIs
- Provides a read-only REST API consumed by the skarnik.by frontend
- Syncs the word index to Typesense for full-text search

## Stack

- **Python 3.13** / **Django 5.2** / **Django REST Framework 3.16.1**
- **MySQL/MariaDB** (production) — SQLite for development/testing
- **Typesense** for full-text search
- **TinyMCE** for rich-text translation editing
- **django-reversion** for change history in the admin

## Quick Start

```bash
# Clone and set up virtual environment
python -m venv ENV
source ENV/bin/activate
pip install -r requirements/development.txt

# Configure secrets (copy template and fill in DB credentials, Typesense key, etc.)
cp secrets.json.example secrets.json  # edit as needed

# Apply migrations
python manage.py migrate --settings=config.settings.development

# Run development server
python manage.py runserver --settings=config.settings.development
```

## Running Tests

```bash
python manage.py test main --settings=config.settings.testing
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/words/<id>/` | Word by primary key |
| `GET /api/words/<direction>/<external_id>/` | Word by direction + external ID |

Directions: `be-ru`, `ru-be`, `tsbm`

## Management Commands

```bash
# Sync Typesense search index
python manage.py sync_typesense

# Fetch stress marks from external API
python manage.py fill_stress_bnk --direction be-ru [--dry-run] [--limit N]

# Copy legacy translations table to words table
python manage.py copy_translations_to_words
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

Select the settings module via `DJANGO_SETTINGS_MODULE` (configured in `.envrc`):

| Module | Use |
|--------|-----|
| `config.settings.development` | Local development |
| `config.settings.testing` | Test runs (in-memory SQLite) |
| `config.settings.production` | Production server |
