from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, viewsets, permissions, status
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (RecipeShoppingCartSerializer, SubscriptionSerializer,
                          IngredientSerializer, RecipeFavoriteSerializer,
                          TagSerializer, RecipeReadSerializer,
                          RecipeCreateSerializer)
from . import serializers
from .filters import RecipeFilter
from .permissions import AuthorAdminOrReadOnly
from users.models import User, Subscription
from recipes.models import (Ingredient, Tag, ShoppingCart, Favorite,
                            IngredientAmount, Recipe)


class ManageFavorite:
    """Содержит логику управления избронными объектами."""

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавляет или удаляет из избранного."""

        try:
            instance = self.get_object()
        except Http404:
            return Response({'message': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)
        if request.method == 'POST':
            try:
                Recipe.objects.get(id=instance.id)
            except Recipe.DoesNotExist:
                return Response(
                    {'message': 'Переданный рецепт не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite_obj, created = Favorite.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=instance.id
            )
            if created:
                favorite_obj.save()
                serializer = RecipeFavoriteSerializer(
                    instance,
                    context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Контент уже находится в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            favorite_obj = Favorite.objects.get(
                user=request.user,
                content_type=content_type,
                object_id=instance.id
            )
            favorite_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response(
                {'message': 'Контент не находится в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def annotate_qs_is_favorite_field(self, queryset):
        """Фильтрует избранные объекты."""

        if self.request.user.is_authenticated:
            is_favorite_subquery = Favorite.objects.filter(
                object_id=OuterRef('pk'),
                user=self.request.user,
                content_type=ContentType.objects.get_for_model(queryset.model)
            )
            queryset = queryset.annotate(
                is_favorite=Exists(is_favorite_subquery))
        return queryset

    @action(
        detail=False,
        methods=('get',),
        url_path='favorites',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorites(self, request):
        """Выдает список избранных для текущего пользователя."""

        queryset = self.get_queryset().filter(is_favorite=True)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManageShopingCart:
    """Содержит логику управления объектами из корзины."""

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавляет или удаляет из корзины."""

        try:
            instance = self.get_object()
        except Http404:
            return Response({'message': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)

        content_type = ContentType.objects.get_for_model(instance)

        serializer = RecipeShoppingCartSerializer(instance,
                                                  context={'request': request})
        if request.method == 'POST':
            shopping_cart_obj, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=instance.id
            )

            if created:
                shopping_cart_obj.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Контент уже находится в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            shopping_cart_obj = ShoppingCart.objects.get(
                user=request.user,
                content_type=content_type,
                object_id=instance.id
            )
            shopping_cart_obj.delete()
            return Response(
                {'message': 'Контент удален из корзины'},
                status=status.HTTP_204_NO_CONTENT
            )
        except ShoppingCart.DoesNotExist:
            return Response(
                {'message': 'Контент не находится в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserList(generics.ListAPIView):
    """Определяет REST методы для работы со списком пользователей."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    """REST метод для чтения деталей пользователя."""

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class CustomUserViewSet(UserViewSet):
    """Определяет дополнителье REST методы для работы с пользователем."""

    def get_recipes_limit(self, request):
        param = request.query_params.get('recipes_limit')
        if not param:
            return None, None

        try:
            return int(param), None
        except ValueError:
            return None, Response(
                {'error': 'Recipes_limit должен быть числом'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=('get',), detail=False, permission_classes=(
            permissions.IsAuthenticated,))
    def subscriptions(self, request):
        """REST метод для вывода списка подписок."""

        user = request.user
        followings = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(followings)

        recipes_limit, err = self.get_recipes_limit(request)
        if err:
            return err

        serializer = SubscriptionSerializer(
            pages, many=True,
            context={'request': request, 'limit': recipes_limit}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=('post', 'delete'), detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        """REST методы для подписки/отписки."""

        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                Subscription.objects.get(user=user, author=author)
                return Response(
                    {'error': 'Вы уже подписаны на пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Subscription.DoesNotExist:
                pass

            recipes_limit, err = self.get_recipes_limit(request)
            if err:
                return err

            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author, context={'request': request, 'limit': recipes_limit})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user, author=author)
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'Вы не подписаны на пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RecipeViewSet(viewsets.ModelViewSet, ManageFavorite, ManageShopingCart):
    """Определяет все REST методы для работы с рецептами."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (AuthorAdminOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateSerializer
        return None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        queryset = self.annotate_qs_is_favorite_field(queryset)
        return queryset

    @action(methods=('get',), detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Формирует и возвращает список покупок в txt формате."""

        ingredients = IngredientAmount.objects\
            .filter(recipe__shopping_cart__user=request.user)\
            .values(
                'ingredient__name',
                'ingredient__units')\
            .order_by('ingredient__name')\
            .annotate(total_amount=Sum('amount'))

        shopping_list = 'Cписок покупок:\n' + '\n'.join([
            f'{ingredient["ingredient__name"]}'
            f' - {ingredient["total_amount"]}'
            f'({ingredient["ingredient__units"]})'
            for ingredient in ingredients
        ])

        return self.build_txt(shopping_list)

    def build_txt(self, shopping_list):
        """Конструирует txt файл из списка ингрилиентов."""

        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientsSearchFilter(filters.SearchFilter):
    """Переопределяет название параметра поиска."""

    search_param = 'name'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Определяет REST методы для работы с рецептами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientsSearchFilter]
    search_fields = ['^name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Определяет REST методы для работы с тегами."""

    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
