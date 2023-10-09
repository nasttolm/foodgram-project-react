from django.contrib import admin

from .models import Recipe, Tag, Ingredient, ShopingList, Favourite

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description', 'ingredients', 
                    'time', 'pub_date', 'author') 
    search_fields = ('name', 'time')
    list_filter = ('tag',)
    empty_value_display = '-пусто-' 


admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(ShopingList)
admin.site.register(Favourite)