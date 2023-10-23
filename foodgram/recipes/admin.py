from django.contrib import admin

from .models import Recipe, Tag, Ingredient, ShoppingCart, Favorite

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description', 'ingredients',
                    'time', 'pub_date', 'author')
    search_fields = ('name', 'time')
    list_filter = ('tag',)
    empty_value_display = '-пусто-'


class IngredientAmountInline(admin.TabularInline):
    model = Ingredient
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units',)
    list_filter = ('name',)
