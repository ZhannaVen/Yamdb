import django_filters as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """
     Настройка фильтрации отображений произведений.
    """
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='contains'
    )
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='contains'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category')
