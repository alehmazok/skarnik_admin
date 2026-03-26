import re

from lxml import html
from django.core.management.base import BaseCommand
from main.models import Word


class Command(BaseCommand):
    help = "Find words with color span pattern in rusbel direction"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be found without making changes",
        )
        parser.add_argument(
            "--word-id",
            type=int,
            default=None,
            help="Process only a specific word ID",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of words to process",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        limit = options.get("limit")
        word_id = options.get("word_id")

        # 1. Находит любые элементы со специфическим цветом
        # 2. Находит ВСЕ теги <a>
        xpath_query = "//*[@data-word and not(@data-link) and contains(text(), ',')]"

        words = Word.objects.filter(direction="rusbel")
        if word_id:
            words = words.filter(pk=word_id)
        if limit:
            words = words[:limit]
        total_count = words.count()
        self.stdout.write(f'Found {total_count} words with direction="rusbel"')

        found_count = 0
        for word in words:
            self.stdout.write(f"Processing word ({word.pk}) `{word.text}`:")
            # Создаем дерево элементов
            tree = html.fromstring(word.translation)

            elements = tree.xpath(xpath_query)

            for el in elements:

                # Получаем текст внутри элемента (учитывая возможные вложенные теги)
                original_text = el.text_content().strip()

                # 1. Записываем текст в новый атрибут data-word
                # el.set("data-word", original_text)

                # 3. Clean up: split by ',', strip spaces, and remove empty strings
                split_words = [w.strip() for w in original_text.split(",") if w.strip()]

                split_words_count = len(split_words)

                if split_words_count > 0:
                    # 2. Очищаем текущее содержимое и вставляем измененный html
                    el.text = None

                for i, split_word in enumerate(split_words):
                    found_count += 1

                    belrus_matches = Word.objects.filter(
                        text__iexact=split_word,
                        direction="belrus",
                        stress__isnull=False,
                    )
                    belrus_count = belrus_matches.count()

                    message = ("  Word: {word}, Matches: {matches}").format(
                        word=split_word,
                        matches=belrus_count,
                    )
                    if belrus_count > 1:
                        self.stdout.write(self.style.WARNING(message))
                    elif belrus_count == 0:
                        self.stdout.write(self.style.ERROR(message))
                    else:
                        stress_value = (
                            belrus_matches[0].stress if belrus_count == 1 else None
                        )
                        link_value = (
                            belrus_matches[0].relative_link
                            if belrus_count == 1
                            else None
                        )
                        external_link_value = (
                            belrus_matches[0].relative_external_link
                            if belrus_count == 1
                            else None
                        )

                        word_html = "<span data-word='{split_word}' data-link='{link}' data-external-link='{external_link}'>{stress}</span>".format(
                            split_word=split_word,
                            link=link_value,
                            external_link=external_link_value,
                            stress=stress_value,
                        )

                        # el.set("data-link", link_value)
                        # el.set("data-external-link", external_link_value)

                        self.stdout.write(message)

                        span = html.fragment_fromstring(word_html)

                        # Identify if NOT the last item to add a separator
                        if i < split_words_count - 1:
                            span.tail = ", "  # Adds the comma AFTER this span

                        el.append(span)

                if "data-word" in el.attrib:
                    del el.attrib["data-word"]

            # Превращаем дерево обратно в строку
            # method="html" сохранит привычный вид тегов
            updated_html = html.tostring(tree, encoding="unicode", method="html")

            # print(updated_html)

            if not dry_run:
                word.translation = updated_html
                word.save(update_fields=["translation"])

        self.stdout.write(
            self.style.SUCCESS(f"Found {found_count} words with the comma pattern")
        )

        if not dry_run:
            self.stdout.write("Processing complete.")
        else:
            self.stdout.write("Dry run complete - no changes made.")
