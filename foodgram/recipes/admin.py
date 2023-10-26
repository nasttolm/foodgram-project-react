from django.contrib import admin

from .models import Recipe, Tag, Ingredient, ShoppingCart, Favorite

admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favorites')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('in_favorites',)
    empty_value_display = '-пусто-'

    def in_favorites(self, obj):
        return obj.favorites.count()


class IngredientAmountInline(admin.TabularInline):
    model = Ingredient
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'units',)
    list_filter = ('name',)
