from django.contrib import admin
from django.utils.html import format_html
from bs4 import BeautifulSoup
from reversion.admin import VersionAdmin

from .admin_filters import LetterListFilter, DirectionListFilter
from .models import Word, Translation


class WordAdmin(VersionAdmin):
    list_display = ("id", "external_id", "direction", "text", "stress", "redirect_to")
    readonly_fields = (
        "id",
        "external_id",
        "letter",
        "direction",
        "translation_html",
    )
    list_display_links = ("id", "external_id")
    list_filter = (LetterListFilter, DirectionListFilter)
    search_fields = ("text", "translation")
    list_per_page = 100

    fieldsets = (
        (
            "Word Information",
            {
                "fields": (
                    "external_id",
                    "letter",
                    "direction",
                    "redirect_to",
                    "text",
                    "stress",
                    "translation",
                    "translation_html",
                ),
            },
        ),
    )

    def translation_html(self, obj: Word):
        if not obj or not obj.translation:
            return "—"
        soup = BeautifulSoup(obj.translation, "html.parser")
        pretty_html = soup.prettify()
        return format_html(
            "<pre style='white-space: pre-wrap; word-break: break-word; font-family: monospace; margin: 0;'>"
            "{}"
            "</pre>",
            pretty_html,
        )

    translation_html.short_description = "Translation HTML"


@admin.register(Translation)
class TranslationAdmin(VersionAdmin):
    list_display = ("id", "external_id", "letter", "direction", "text")
    readonly_fields = (
        "id",
        "external_id",
        "letter",
        "direction",
        "text",
        "translation",
    )
    list_display_links = ("id", "external_id")
    list_filter = ("letter", "direction")
    search_fields = ("text", "translation")
    list_per_page = 100

    fieldsets = (
        (
            "Translation Information",
            {
                "fields": ("external_id", "letter", "direction", "text", "translation"),
            },
        ),
    )


admin.site.register(Word, WordAdmin)
