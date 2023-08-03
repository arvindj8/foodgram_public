from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    """Команда для импорта тегов в БД."""
    help = 'Tags loading'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'супы', 'color': '#CD5C5C', 'slug': 'soup'},
            {'name': 'гарниры', 'color': '#228B22', 'slug': 'garnish'},
            {'name': 'салаты', 'color': '#87CEFA', 'slug': 'salad'},
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Теги загружены в БД'))
