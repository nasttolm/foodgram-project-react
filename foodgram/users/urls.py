from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import FoodgramUserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('users', FoodgramUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls.authtoken')),
    path('api-token-auth/', views.obtain_auth_token),
]