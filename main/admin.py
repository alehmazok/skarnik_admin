from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Word


class WordAdmin(VersionAdmin):
    list_display = ('id', 'external_id', 'letter', 'direction', 'text')
    readonly_fields = ('id', 'external_id', 'letter', 'direction')
    list_display_links = ('id', 'external_id')
    list_filter = ('letter', 'direction')
    search_fields = ('text', 'translation')
    list_per_page = 100

    fieldsets = (
        ('Word Information', {
            'fields': ('external_id', 'letter', 'direction', 'text', 'translation'),
        }),
    )


admin.site.register(Word, WordAdmin)
