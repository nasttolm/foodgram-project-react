from drf_base64.fields import Base64ImageField
from rest_framework import serializers 
from rest_framework.relations import SlugRelatedField 
from rest_framework.validators import UniqueTogetherValidator 
from djoser.serializers import UserCreateSerializer, UserSerializer
 
from recipes.models import Recipe, Tag, Ingredient, Achievement, IngredientAmount, Favorite, ShoppingCart

from django.shortcuts import get_object_or_404

from users.models import User, Subscription

# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('__all__') 

class AchievementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Achievement
        fields = ('id', 'name') 

class CustomUserCreateSerializer(UserCreateSerializer):

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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    # recipe = serializers.StringRelatedField(read_only=True)
    # achievements = AchievementSerializer(read_only=True, many=True)
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

# class RecipeSerializer(serializers.ModelSerializer):
#     author = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
#     image = Base64ImageField()
#     is_favorite = serializers.BooleanField(read_only=True)
#     # ingredients = IngredientAmountCreateSerializer(many=True)
#     class Meta:
#         fields = '__all__'
#         model = Recipe
#     # def get_is_favorited(self, obj):
#     #     return (
#     #         self.context.get('request').user.is_authenticated
#     #         and Favorite.objects.filter(user=self.context['request'].user,
#     #                                     recipe=obj).exists()
#     #     )
#     def add_tags_ingredients(self, recipe, tags, ingredients):
#         recipe.tags.set(tags)
#         IngredientAmount.objects.bulk_create(
#             [IngredientAmount(
#                 recipe=recipe,
#                 ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
#                 amount=ingredient['amount']
#             ) for ingredient in ingredients]
#         )

#     # def create(self, validated_data):
#     #     ingredients = validated_data.pop('ingredients')
#     #     tags = validated_data.pop('tags')
#     #     recipe = Recipe.objects.create(**validated_data)
#     #     self.add_tags_ingredients(recipe, tags, ingredients)
#     #     return recipe

#     def update(self, instance, validated_data):
#         ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
#         instance.ingredients.clear()
#         instance.tags.clear()
#         self.add_tags_ingredients(instance, tags, ingredients)
#         return super().update(instance, validated_data)

#     def to_representation(self, instance):
#         return RecipeReadSerializer(instance,
#                                     context=self.context).data


class BriefRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):

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

    def get_recipes_count(self, obj):
        return obj.recipes.count()


    # user = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True,
    #     default=serializers.CurrentUserDefault()
    # )
    # following = SlugRelatedField(
    #     slug_field='author__username',
    #     queryset=User.objects.all()
    # )

    # class Meta:
    #     fields = ('user', 'following')
    #     model = Subscription

    #     validators = [
    #         UniqueTogetherValidator(
    #             queryset=Subscription.objects.all(),
    #             fields=('user', 'following')
    #         )
    #     ]
    # def validate(self, data):
    #     if self.context['request'].user == data['following']:
    #         raise serializers.ValidationError(
    #             'Нельзя подписаться на самого себя!')
    #     return data

class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    units = serializers.ReadOnlyField(
        source='ingredient.units'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id',
                  'name',
                  'units',
                  'amount'
                  )


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
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

# class CartItemSerializer(serializers.ModelSerializer):
#     recipe = RecipeSerializer()
 
#     class Meta:
#         model = CartItem
#         fields = '__all__'

class RecipeReadSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, read_only=True, source='amounts')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(user=self.context['request'].user,
                                        object_id=obj.id).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user,
                object_id=obj.id).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
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

    def add_tags_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self.add_tags_ingredients(instance, tags, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data