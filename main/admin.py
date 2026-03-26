from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from bs4 import BeautifulSoup
from reversion.admin import VersionAdmin

from .admin_filters import LetterListFilter, DirectionListFilter
from .models import Word, Translation
from .supabase_sync import push_word, pull_word


def _push_to_supabase(modeladmin, request, queryset):
    success, errors = 0, []
    for word in queryset:
        try:
            push_word(word)
            success += 1
        except Exception as e:
            errors.append(f"{word}: {e}")
    if success:
        modeladmin.message_user(request, f"Pushed {success} word(s) to Supabase.", messages.SUCCESS)
    for err in errors:
        modeladmin.message_user(request, err, messages.ERROR)


_push_to_supabase.short_description = "Push to Supabase"


def _pull_from_supabase(modeladmin, request, queryset):
    success, errors = 0, []
    for word in queryset:
        try:
            pull_word(word)
            success += 1
        except Exception as e:
            errors.append(f"{word}: {e}")
    if success:
        modeladmin.message_user(request, f"Pulled {success} word(s) from Supabase.", messages.SUCCESS)
    for err in errors:
        modeladmin.message_user(request, err, messages.ERROR)


_pull_from_supabase.short_description = "Pull from Supabase"


class WordAdmin(VersionAdmin):
    list_display = ("id", "external_id", "direction", "text", "stress", "redirect_to")
    readonly_fields = (
        "id",
        "external_id",
        "letter",
        "direction",
        "translation_html",
        "supabase_sync_buttons",
    )
    list_display_links = ("id", "external_id")
    list_filter = (LetterListFilter, DirectionListFilter)
    search_fields = ("^text", "external_id")
    list_per_page = 100
    actions = [_push_to_supabase, _pull_from_supabase]

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
        (
            "Supabase",
            {
                "fields": ("supabase_sync_buttons",),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/push-supabase/",
                self.admin_site.admin_view(self._push_view),
                name="word-push-supabase",
            ),
            path(
                "<int:pk>/pull-supabase/",
                self.admin_site.admin_view(self._pull_view),
                name="word-pull-supabase",
            ),
        ]
        return custom + urls

    def _push_view(self, request, pk):
        word = get_object_or_404(Word, pk=pk)
        try:
            push_word(word)
            self.message_user(request, f'"{word}" pushed to Supabase.', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Push failed: {e}", messages.ERROR)
        return redirect(reverse("admin:main_word_change", args=[pk]))

    def _pull_view(self, request, pk):
        word = get_object_or_404(Word, pk=pk)
        try:
            pull_word(word)
            self.message_user(request, f'"{word}" pulled from Supabase.', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Pull failed: {e}", messages.ERROR)
        return redirect(reverse("admin:main_word_change", args=[pk]))

    def supabase_sync_buttons(self, obj):
        if not obj or not obj.pk:
            return "—"
        push_url = reverse("admin:word-push-supabase", args=[obj.pk])
        pull_url = reverse("admin:word-pull-supabase", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button">⬆️ Push to Supabase</a>&nbsp;'
            '<a href="{}" class="button">⬇️ Pull from Supabase</a>',
            push_url,
            pull_url,
        )

    supabase_sync_buttons.short_description = "Supabase Sync"

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
