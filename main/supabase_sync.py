from django.conf import settings
from supabase import create_client

TABLE = "main_word"


def _client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def push_word(word) -> None:
    """Upsert a local Word to Supabase, overwriting on (external_id, direction) conflict."""
    data = {
        "external_id": word.external_id,
        "letter": word.letter,
        "direction": word.direction,
        "text": word.text,
        "translation": word.translation,
        "redirect_to": word.redirect_to,
        "stress": word.stress,
    }
    _client().table(TABLE).upsert(data, on_conflict="external_id,direction").execute()


def pull_word(word) -> None:
    """Fetch a Word from Supabase by (external_id, direction) and overwrite local fields."""
    response = (
        _client()
        .table(TABLE)
        .select("*")
        .eq("external_id", word.external_id)
        .eq("direction", word.direction)
        .execute()
    )
    if not response.data:
        raise ValueError(
            f"Word (external_id={word.external_id}, direction={word.direction}) not found in Supabase."
        )
    row = response.data[0]
    word.letter = row["letter"]
    word.text = row["text"]
    word.translation = row["translation"]
    word.redirect_to = row.get("redirect_to")
    word.stress = row.get("stress")
    word.save()
