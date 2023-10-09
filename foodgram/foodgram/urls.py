from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/', include('users.urls', namespace='users')),
    # path('api/', include('api.urls', namespace='api')),
    # path('admin/', admin.site.urls),
]

# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('api.urls', namespace='api')),
# ]