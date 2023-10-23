from . import serializers
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Ingredient, Tag, ShoppingCart, Favorite
from recipes.models import IngredientAmount, Recipe
from rest_framework import filters, viewsets, permissions, status
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User, Subscription

from .filters import RecipeFilter
from .serializers import (SubscriptionSerializer, IngredientSerializer,
                          TagSerializer, RecipeReadSerializer,
                          RecipeCreateSerializer)


class ManageFavorite:
    @action(
      detail=True,
      methods=['post', 'delete'],
      url_path='favorite',
      permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)
        favorite_obj, created = Favorite.objects.get_or_create(
            user=request.user, content_type=content_type, object_id=instance.id
        )

        if request.method == 'POST':
            if created:
                favorite_obj.save()
                return Response(
                    {'message': 'Контент добавлен в избранное'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': 'Контент уже находится в избранном'},
                    status=status.HTTP_201_CREATED
                )
        else:
            favorite_obj.delete()
            return Response(
                {'message': 'Контент удален из избранного'},
                status=status.HTTP_200_OK
            )

    def annotate_qs_is_favorite_field(self, queryset):
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
        methods=['get'],
        url_path='favorites',
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def favorites(self, request):
        queryset = self.get_queryset().filter(is_favorite=True)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManageShopingCart:
    @action(
      detail=True,
      methods=['post', 'delete'],
      url_path='shopping_cart',
      permission_classes=[permissions.IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        instance = self.get_object()
        content_type = ContentType.objects.get_for_model(instance)
        shopping_cart_obj, created = ShoppingCart.objects.get_or_create(
            user=request.user, content_type=content_type, object_id=instance.id
        )

        if request.method == 'POST':
            if created:
                shopping_cart_obj.save()
                return Response(
                    {'message': 'Контент добавлен в корзину'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': 'Контент уже находится в корзине'},
                    status=status.HTTP_201_CREATED
                )
        else:
            shopping_cart_obj.delete()
            return Response(
                {'message': 'Контент удален из корзины'},
                status=status.HTTP_200_OK
            )


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class CustomUserViewSet(UserViewSet):

    @action(methods=['get'], detail=False, permission_classes=(
            permissions.IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        followings = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(followings)
        serializer = SubscriptionSerializer(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author, context={'request': request})
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
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeCreateSerializer
        return None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        queryset = self.annotate_qs_is_favorite_field(queryset)
        return queryset

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
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
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientsSearchFilter(filters.SearchFilter):
    search_param = 'name'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientsSearchFilter]
    search_fields = ['$name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
