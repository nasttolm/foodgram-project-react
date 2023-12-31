from django.core.exceptions import ObjectDoesNotExist
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Recipe, Tag, Ingredient, Achievement,
                            IngredientAmount, Favorite, ShoppingCart)
from users.models import User, Subscription


class AchievementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Achievement
        fields = ('id', 'name')


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверка, что переданный пользователь подписан на этого
           пользователя."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    measurement_unit = serializers.CharField(source='units')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода кортоткого описания рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для модели подписки."""

    recipes = BriefRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        limit = self.context.get('limit')
        if limit:
            ret['recipes'] = ret['recipes'][:limit]
        return ret

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода количества ингредиентов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.units'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if not (1 <= value <= 30000):
            raise serializers.ValidationError(
                'Количество должно быть целым числом от 1 до 30 000'
            )
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецепта."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, read_only=True, source='amounts')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def get_is_favorited(self, obj):
        """Проверяет добавлен ли рецепт в избранное."""

        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        object_id=obj.id).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет добавлен ли рецепт в корзину покупок."""

        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                object_id=obj.id).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientAmountCreateSerializer(many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'name')
            )
        ]

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Ингредиенты должны быть указаны.')
        seen = set()
        dupes = [x['id'] for x in value if x['id'] in seen
                 or seen.add(x['id'])]
        if len(dupes) > 0:
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.')
        return value

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Теги должны быть указаны.')
        seen = set()
        dupes = [x for x in value if x in seen
                 or seen.add(x)]
        if len(dupes) > 0:
            raise serializers.ValidationError(
                'Теги не должны повторяться.')
        return value

    def add_tags_ingredients(self, recipe, tags, ingredients):
        """Добавляет теги и ингридиенты в рецепт."""

        recipe.tags.set(tags)
        try:
            prepared_ingredient = [(
                Ingredient.objects.get(id=ingredient['id']),
                ingredient['amount']) for ingredient in ingredients]
        except ObjectDoesNotExist:
            raise ValidationError('Ингредиент не существует.')

        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=x[0],
                amount=x[1]
            ) for x in prepared_ingredient]
        )

    def create(self, validated_data):
        """Создает рецепт из данных, переданных пользователем."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Редактирует рецепт данными переданными пользователем."""

        ingredients = validated_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                  'Ингридиенты не указаны.')

        tags = validated_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                  'Теги не указаны.')
        cooking_time = validated_data.get('cooking_tim')
        if not cooking_time:
            raise serializers.ValidationError(
                  'Время готовки не указаны.')
        text = validated_data.get('text')
        if not text:
            raise serializers.ValidationError(
                  'Текст пустой.')
        instance.ingredients.clear()
        instance.tags.clear()
        self.add_tags_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает read сереализатор для данной модели."""

        return RecipeReadSerializer(instance,
                                    context=self.context).data


class RecipeShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта добавленного в корзину."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта добавленного в избранное."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
