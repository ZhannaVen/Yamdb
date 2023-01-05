from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Category name'
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Genre name'
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Composition title (name)',
    )
    year = models.IntegerField(
        validators=[validate_year],
        db_index=True,
        verbose_name='Year of creation',
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Description'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        through='GenreTitle',
        verbose_name='Genre'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='title_category',
        verbose_name='Category'
    )

    class Meta:
        verbose_name = 'Composition'
        verbose_name_plural = 'Compositions'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Composition'
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Review text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Author'
    )
    score = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
        verbose_name='Evaluation of composition'
    )
    pub_date = models.DateTimeField(
        'Date of creation',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = [models.UniqueConstraint(
            fields=['title', 'author'],
            name='all_keys_unique_together'
        )]
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return self.text[settings.STRING_LEN]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Composition'
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Comment text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Author'
    )
    pub_date = models.DateTimeField(
        'Date of creation',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return self.text[settings.STRING_LEN]
