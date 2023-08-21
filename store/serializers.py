from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from .models import *
from core.serializers import UserSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(Product_id= product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductAttributesSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductAttributes.objects.create(Product_id= product_id, **validated_data)
        
    class Meta:
        model = ProductAttributes
        fields = ['id', 'attribute']

class ProductPowersSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductPowers.objects.create(Product_id= product_id, **validated_data)

    class Meta:
        model = ProductPowers
        fields = [ 'id', 'unit', 'power']

class SimpleCollectionSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    attributes = ProductAttributesSerializer(many=True, read_only=True)
    powers = ProductPowersSerializer(many=True, read_only=True)
    cart_quantity = serializers.SerializerMethodField()

    def get_cart_quantity(self, product):
        user = self.context['request'].user
        if user.is_authenticated:
            try:
                customer = Customer.objects.only(
                'id').get(user_id=user.id)
                newest_cart = Cart.objects.filter(customer=customer).order_by('-created_at').first()
                cart_item = CartItem.objects.get(cart=newest_cart, product=product)
                return cart_item.quantity
            except CartItem.DoesNotExist:
                return None
        return None

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'introduction', 'powers', 'slug', 'inventory',
                  'unit_price', 'cart_quantity', 'group', 'images', 'attributes']

    # TODO if you wanna add price with tax uncomment 👇🏻 code and add 'price_with_tax' to the fields

    # price_with_tax = serializers.SerializerMethodField(
    #     method_name='calculate_tax')

    # def calculate_tax(self, product: Product):
    #     return product.unit_price * Decimal(1.1)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'images']

class GroupSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    class Meta:
        model = Group
        fields = ['id', 'title', 'slug', 'image','collection', 'description', 'product_count', 'products']

    product_count = serializers.IntegerField(read_only=True)

    def get_products(self, obj):
        # get the related products for the current Group object
        queryset = obj.products.order_by('id')[:4]  # retrieve only the first 4 products

        # serialize the queryset using the SimpleProductSerializer defined in your code
        serializer = SimpleProductSerializer(queryset, many=True)
        return serializer.data

class SimpleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'title','collection', 'image']

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'groups_count', 'featured_group']

    groups_count = serializers.IntegerField(read_only=True)

class MainPageCollectionSerializer(serializers.ModelSerializer):
    featured_group = SimpleGroupSerializer()
    class Meta:
        model = Collection
        fields = ['id', 'title', 'featured_group']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'customer']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        try: 
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    #user_id = serializers.IntegerField(read_only=True)
    user = UserSerializer( read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user', 'nationalid', 'state', 'city', 'adress', 'job', 'edu', 'is_complete']

class SimpleCustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Customer
        fields = ['id', 'nationalid', 'user']

class ChatSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        support_id = self.context['support_id']
        return Chat.objects.create(support_id= support_id, **validated_data)
        
    class Meta:
        model = Chat
        fields = ['id', 'name', 'description','date']

class SupportSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    chat = ChatSerializer(many=True, read_only=True)
    class Meta:
        model = Support
        fields = ['id', 'title', 'description', 'chat', 'status', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user.id
        support = Support.objects.create(user_id=user, **validated_data)
        return support

class GuaranteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guarantee
        fields = ['id', 'serial',  'product', 'is_active', 'mobile', 'created_date', 'activated_date']

class OrderSpecialProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'group', 'images']

class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderSpecialProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']

class OrderStatusSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        order_id = self.context['order_id']
        return OrderStatus.objects.create(order_id= order_id, **validated_data)
    class Meta:
        model = OrderStatus
        fields = ['id','payment_status', 'status_change']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    status = OrderStatusSerializer(many=True, read_only = True)
    last_status = serializers.SerializerMethodField()

    def get_total_price(self, order):
        return sum([item.quantity * item.unit_price for item in order.items.all()])
    
    def get_last_status(self, order):
        last_status = order.status.order_by('-status_change').first()
        if last_status:
            return OrderStatusSerializer(last_status).data['payment_status']
        return None

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'status', 'last_status', 'items', 'total_price']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['laststatus'] 


    def update(self, instance, validated_data):
        order_id = self.context['order_id']

        # Update Order
        order = Order.objects.get(id=order_id)
        order.laststatus = validated_data['laststatus']
        order.save()

        # Create new OrderStatus
        order_status = OrderStatus.objects.create(
            order_id=order_id,
            payment_status=validated_data['laststatus']
        )


        return {'order': OrderSerializer(order).data, 'order_status': OrderStatusSerializer(order_status).data}

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            OrderStatus.objects.create(order = order)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'image','title', 'description', 'writer', 'date']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class FastcallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fastcall
        fields = '__all__'