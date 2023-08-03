import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиентов в БД."""
    help = "import from ingredients.csv"

    def handle(self, *args, **kwargs):
        with open('recipes/data/ingredients.csv',
                  'r', encoding='utf-8') as file:
            file_reader = csv.reader(file)
            next(file_reader)

            for row in file_reader:
                name, unit_of_measurement = row
                Ingredient.objects.get_or_create(
                    name=name,
                    unit_of_measurement=unit_of_measurement
                )
        self.stdout.write(self.style.SUCCESS('Ингредиенты загружены в БД'))
