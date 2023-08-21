from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission
from store.pagination import *
from django.db.models.aggregates import Count
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status, permissions
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
from .filters import *
from .models import *
from .serializers import *
from .services import clean_expired_carts, clean_old_carts
import ghasedakpack
import asyncio

# SMS Panel Config
token = '54c3316602660f55689c533885c993adf5367dce14a8491cfd530fb2401b0a22'
phone = {'09144892281','09144244622'}

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images', 'attributes').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update', 'id']
    ordering = ['id']

    def get_queryset(self):
        queryset = Product.objects.prefetch_related('images', 'attributes').all()
        queryset = queryset.annotate(title_int=Cast('title', output_field=IntegerField()))
        queryset = queryset.order_by('title_int')
        return queryset

    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    def get_serializer_context(self):
         return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
         return ProductImage.objects.filter(Product_id = self.kwargs['product_pk'])

class ProductAttributesViewSet(ModelViewSet):
    serializer_class = ProductAttributesSerializer
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]
        
    def get_serializer_context(self):
         return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
         return ProductAttributes.objects.filter(Product_id = self.kwargs['product_pk'])

class ProductPowersViewSet(ModelViewSet):
    serializer_class = ProductPowersSerializer

    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
         return ProductPowers.objects.filter(Product_id = self.kwargs['product_pk'])

class SimpleProductViewSet(ModelViewSet):
    serializer_class = SimpleProductSerializer
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    def get_serializer_context(self):
         return {'group_id': self.kwargs['group_pk']}

    def get_queryset(self):
         return Product.objects.filter(Group_id = self.kwargs['group_pk'])

class GroupViewSet(ModelViewSet):
    queryset = Group.objects.annotate(
        products_count=Count('products')).prefetch_related('products').all()
    serializer_class = GroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = GroupFilter
    search_fields = ['title']
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    def get_serializer_context(self):
        return {'request': self.request}
    
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        groups_count=Count('groups')).all()
    serializer_class = CollectionSerializer
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    def get_serializer_context(self):
        return {'request': self.request}

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method in ['DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            customer = Customer.objects.only(
            'id').get(user_id=user.id)
            serializer.save(customer=customer)
        else:
            serializer.save(customer=None)
        
        clean_expired_carts()
        clean_old_carts()

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
   
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects \
                .filter(cart_id=self.kwargs['cart_pk']) \
                .select_related('product')

class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset =Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':   
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class SupportViewSet(ModelViewSet):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SupportFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Support.objects.all()
        return Support.objects.filter(user=user)
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def to_representation(self, instance):
        """
        Exclude user field in POST requests.
        """
        request = self.context.get('request')
        if request.method == 'POST':
            self.fields.pop('user')
        return super().to_representation(instance)
    
    def create(self, request, *args, **kwargs):
        serializer = SupportSerializer(
            data=request.data,
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        support = serializer.save()
        serializer = SupportSerializer(support)
        return Response(serializer.data)
    
class ChatViewSet(ModelViewSet):
    serializer_class = ChatSerializer

    def get_permissions(self):
        if self.request.method in ['PUT','PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Chat.objects.filter(support_id=self.kwargs['support_pk'])

    def get_serializer_context(self):
        return {'support_id': self.kwargs['support_pk']}

class GuaranteeViewSet(ModelViewSet):
    queryset = Guarantee.objects.all()
    serializer_class = GuaranteeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['serial']

    def get_permissions(self):
        if self.request.method in ['POST', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filter_backends = [DjangoFilterBackend, SearchFilter, LastStatusFilterBackend]
    search_fields = ['id']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        customer_id = serializer.data['customer']
        customer = Customer.objects.get(id=customer_id)
        user = User.objects.get(customer=serializer.data['customer'])
        total_price = serializer.data['total_price']
        message = 'سفارش جدید ثبت شده است\n'
        message += f"مشتری: {customer}\n"
        message += f"شماره تلفن مشتری: {user}\n"
        message += f"قیمت کل خرید: {total_price}\n"
        message += f"مشاهده اطلاعات کامل سفارش:\n"
        message += f"http://213.176.29.118/admin/orderscheacker/{serializer.data['id']}"
        sms = ghasedakpack.Ghasedak(token)
        sms.send({'message':message, 'receptor' : phone, 'linenumber': '300002525'})
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only(
            'id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

class OrderStatusViewSet(ModelViewSet):
    serializer_class = OrderStatusSerializer
    
    def get_permissions(self):
        return [IsAdminOrReadOnly()]
        
    def get_serializer_context(self):
         return {'order_id': self.kwargs['order_pk']}

    def get_queryset(self):
         return OrderStatus.objects.filter(order_id = self.kwargs['order_pk'])

class NewsViewSet(ModelViewSet):

    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['date']

class MainPageViewSet(ListModelMixin, GenericViewSet):
    queryset = Collection.objects.all()
    serializer_class = MainPageCollectionSerializer
    
    from django.http import JsonResponse
    from django.contrib.auth.decorators import login_required
    from .models import Notification
    
class NotificationsViewSet(ModelViewSet):

    def get_permissions(self):
        return [IsAdminOrReadOnly()]

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']

class FastcallViewSet(ModelViewSet):
    queryset = Fastcall.objects.all()
    serializer_class = FastcallSerializer

    def get_permissions(self):
        if self.request.method in ['GET','DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]