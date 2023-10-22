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



# from django.contrib import admin

# from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
#                      ShoppingCart, Tag)

# admin.site.register(Tag)
# admin.site.register(ShoppingCart)
# admin.site.register(Favorite)
# admin.site.register(IngredientAmount)


# class IngredientAmountInline(admin.TabularInline):
#     model = IngredientAmount
#     min_num = 1


# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'author', 'in_favorites')
#     list_filter = ('name', 'author', 'tags')
#     readonly_fields = ('in_favorites',)
#     inlines = (IngredientAmountInline,)

#     def in_favorites(self, obj):
#         return obj.favorites.count()


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'measurement_unit',)
#     list_filter = ('name',)