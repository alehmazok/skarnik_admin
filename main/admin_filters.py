from django.contrib import admin


class LetterListFilter(admin.SimpleListFilter):
    title = 'Літара'

    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        return [
            ('А', 'А'),
            ('Б', 'Б'),
            ('В', 'В'),
            ('Г', 'Г'),
            ('Д', 'Д'),
            ('Е', 'Е'),
            ('Ж', 'Ж'),
            ('З', 'З'),
            ('І', 'І'),
            ('И', 'И'),
            ('Й', 'Й'),
            ('К', 'К'),
            ('Л', 'Л'),
            ('М', 'М'),
            ('Н', 'Н'),
            ('О', 'О'),
            ('П', 'П'),
            ('Р', 'Р'),
            ('С', 'С'),
            ('Т', 'Т'),
            ('У', 'У'),
            ('Ф', 'Ф'),
            ('Х', 'Х'),
            ('Ц', 'Ц'),
            ('Ч', 'Ч'),
            ('Ш', 'Ш'),
            ('Щ', 'Щ'),
            ('Э', 'Э'),
            ('Ю', 'Ю'),
            ('Я', 'Я'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(letter__iexact=value)
        return queryset


class DirectionListFilter(admin.SimpleListFilter):
    title = 'Слоўнік'

    parameter_name = 'direction'

    def lookups(self, request, model_admin):
        return [
            ('belrus', 'БЕЛ-РУС'),
            ('rusbel', 'РУС-БЕЛ'),
            ('tsbm', 'ТСБМ'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(direction__iexact=value)
        return queryset
