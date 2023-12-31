from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для отображения избранного и списка покупок."""

    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all()
                                             )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_favorited_filter(self, queryset, name, value):
        """Фильтр для отображения избранных рецептов для пользователя."""

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """Фильтр для отображения рецептов, добавленных в корзину
           пользователя."""

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
