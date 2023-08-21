from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from likes.filters import *
from .models import *
from .serializers import *

# Create your views here.
class LikedItemViewSet(ModelViewSet):
    queryset = LikedItem.objects.all()
    serializer_class = LikedItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LikedItemFilter

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]
