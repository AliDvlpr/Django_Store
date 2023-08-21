from rest_framework.viewsets import ModelViewSet
from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission
from .models import *
from .serializers import *
# Create your views here.
class ImageViewSet(ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]