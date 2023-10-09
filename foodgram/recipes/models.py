from django.db import models

from users.models import User

class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200
    )
    color = models.CharField(
        'Цветовой код тега',
        max_length=200
    )
    slug = models.SlugField(
        'Слаг',
        unique=True
    )
    def __str__(self): 
        return self.name

class Ingredient(models.Model):
    name = models.CharField(
        'Название ингридиента',
        max_length=200
    )
    # quantity = 
    units = models.CharField(
        'Единицы измерения',
        max_length=200
    )
    def __str__(self):
        return f'{self.name}, {self.units}'

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    name = models.CharField(
        'Название рецепта', 
        max_length=200
    )
    image = models.ImageField( 
        'Изображение',
        upload_to='recipes/', 
        blank=True 
    )
    description = models.TextField(
        'Описание рецепта'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиенты',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Теги',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    # cooking_time = 
    def __str__(self): 
        return self.name


class ShopingList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopingList'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopingList'
    )


class Favourite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favourites'
    )


# class Subscription(models.Model):
#     subscription_id =
#     user_id =

# class Follow(models.Model): 
#     user = models.ForeignKey( 
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='follower' 
#     )
#     author = models.ForeignKey( 
#         User, 
#         on_delete=models.CASCADE, 
#         related_name='following' 
#     )

#     def __str__(self): 
#         return f'{self.user} is subscribed to the {self.author}' 