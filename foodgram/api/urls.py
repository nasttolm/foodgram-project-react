from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (TagViewSet, RecipeViewSet, IngredientViewSet,
                    CustomUserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
]
