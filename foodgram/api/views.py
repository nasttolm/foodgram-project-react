from .models import Recipe
from .serializers import RecipeSerializer
from django.shortcuts import get_object_or_404 
from rest_framework import filters, mixins, viewsets 
from rest_framework import viewsets 
from rest_framework.pagination import LimitOffsetPagination 
from rest_framework.permissions import IsAuthenticatedOrReadOnly 
from rest_framework import generics
from . import serializers
from users.models import User

from .permissions import IsAuthorOrReadOnly 
from .serializers import (RecipeSerializer, FollowSerializer) 

from posts.models import Recipe

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

class ResipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    
    def perform_create(self, serializer): 
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
 

 class FollowViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, 
                    viewsets.GenericViewSet): 
    serializer_class = FollowSerializer 
    filter_backends = (filters.SearchFilter, ) 
    search_fields = ('following__username', ) 

    def get_queryset(self): 
        return self.request.user.follower 

    def perform_create(self, serializer): 
        serializer.save(user=self.request.user) 

     

 

    