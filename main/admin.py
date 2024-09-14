from django.contrib import admin
from reversion.admin import VersionAdmin

from .admin_filters import LetterListFilter, DirectionListFilter
from .models import Word, Translation


class WordAdmin(VersionAdmin):
    list_display = ('id', 'external_id', 'letter', 'direction', 'text')
    readonly_fields = ('id', 'external_id', 'letter', 'direction')
    list_display_links = ('id', 'external_id')
    list_filter = (LetterListFilter, DirectionListFilter)
    search_fields = ('text', 'translation')
    list_per_page = 100

    fieldsets = (
        ('Word Information', {
            'fields': ('external_id', 'letter', 'direction', 'text', 'translation'),
        }),
    )


@admin.register(Translation)
class TranslationAdmin(VersionAdmin):
    list_display = ('id', 'external_id', 'letter', 'direction', 'text')
    readonly_fields = ('id', 'external_id', 'letter', 'direction', 'text', 'translation')
    list_display_links = ('id', 'external_id')
    list_filter = ('letter', 'direction')
    search_fields = ('text', 'translation')
    list_per_page = 100

    fieldsets = (
        ('Translation Information', {
            'fields': ('external_id', 'letter', 'direction', 'text', 'translation'),
        }),
    )


admin.site.register(Word, WordAdmin)
