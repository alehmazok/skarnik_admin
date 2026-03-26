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

        handled_xpath_query = "//*[@data-word]"

        # 1. Находит любые элементы со специфическим цветом
        # 2. Находит ВСЕ теги <a>
        xpath_query = "//*[contains(@style, 'color: #831b03')] | //*[contains(@color, '#831b03')] | //a"

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

            handled_elements = tree.xpath(handled_xpath_query)

            if handled_elements:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Word ({word.pk}) `{word.text}` already has handled elements"
                    )
                )
                continue

            elements = tree.xpath(xpath_query)

            for el in elements:
                found_count += 1

                # Получаем текст внутри элемента (учитывая возможные вложенные теги)
                original_text = el.text_content().strip()

                # 1. Записываем текст в новый атрибут data-word
                el.set("data-word", original_text)

                belrus_matches = Word.objects.filter(
                    text__iexact=original_text,
                    direction="belrus",
                    stress__isnull=False,
                )
                belrus_count = belrus_matches.count()

                message = ("  Tag: {tag}, Matches: {matches}:").format(
                    pk=word.pk,
                    tag=el.values(),
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
                        belrus_matches[0].relative_link if belrus_count == 1 else None
                    )
                    external_link_value = (
                        belrus_matches[0].relative_external_link
                        if belrus_count == 1
                        else None
                    )

                    el.set("data-link", link_value)
                    el.set("data-external-link", external_link_value)

                    # 2. Очищаем текущее содержимое и вставляем измененный текст
                    # В lxml .text меняет только непосредственный текст внутри тега
                    # for child in el.getchildren():
                    #     el.remove(child)
                    el.text = stress_value

                    self.stdout.write(message)

            # Превращаем дерево обратно в строку
            # method="html" сохранит привычный вид тегов
            updated_html = html.tostring(tree, encoding="unicode", method="html")

            # print(updated_html)

            if not dry_run:
                word.translation = updated_html
                word.save(update_fields=["translation"])

        self.stdout.write(
            self.style.SUCCESS(f"Found {found_count} words with the color span pattern")
        )

        if not dry_run:
            self.stdout.write("Processing complete.")
        else:
            self.stdout.write("Dry run complete - no changes made.")
