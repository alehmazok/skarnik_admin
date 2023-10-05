from django.contrib import admin

from .models import Word


class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'letter', 'direction', 'text')
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
