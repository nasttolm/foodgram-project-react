from django.urls import include, path
# from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, RecipeViewSet, IngredientViewSet, CustomUserViewSet
# , UserDetail

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet, basename='user')

# router.register('users', UserDetail, basename='user')

urlpatterns = [
    # path('users/', views.UserList.as_view()),
    # path('users/<int:pk>/', views.UserDetail.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('auth/', include('djoser.urls.authtoken')),
]

# urlpatterns = format_suffix_patterns(urlpatterns)