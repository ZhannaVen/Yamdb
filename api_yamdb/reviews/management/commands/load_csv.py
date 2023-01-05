from csv import DictReader

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title

User = get_user_model()

DATASET = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    GenreTitle: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    """Loading data into the database from the corresponding csv
    files is performed by the python manage.py load_csv command.
    """
    def handle(self, *args, **kwargs):
        try:
            for model, file_name in DATASET.items():
                with open(
                    f'{settings.BASE_DIR}/static/data/{file_name}',
                    'r',
                    encoding='utf-8'
                ) as csv_data:
                    reader = DictReader(csv_data)
                    model.objects.bulk_create(
                        model(**data) for data in reader)
                    csv_data.close()
            self.stdout.write(self.style.SUCCESS('All data is loaded'))
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(
                    f'There is an error in loading data {file_name}: {error}'))
