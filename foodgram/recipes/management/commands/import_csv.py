import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        with open('ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            Ingredient.objects.bulk_create(
                [Ingredient(
                    name=row[0],
                    units=row[1]
                ) for row in reader]
            )
        print('Загрузка завершена.')
