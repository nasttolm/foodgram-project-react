from django.urls import include, path
# from rest_framework.routers import DefaultRouter
# from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
# from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'api'

# router = DefaultRouter()
# router.register('tags', TagViewSet)
# router.register('ingredients', IngredientViewSet)
# router.register('recipes', RecipeViewSet)

urlpatterns = [
    # path('users/', views.UserList.as_view()),
    # path('users/<int:pk>/', views.UserDetail.as_view()),
    # path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('', include('djoser.urls.authtoken')),
    # path('api-token-auth/', views.obtain_auth_token),
]

# urlpatterns = format_suffix_patterns(urlpatterns)