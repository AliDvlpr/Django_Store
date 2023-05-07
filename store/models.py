import random
from django.contrib import admin
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4, uuid5
from .validators import validate_file_size
from core.models import User


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_group = models.ForeignKey(
        'Group', on_delete=models.SET_NULL, null=True, related_name='+', blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']

class Group(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+', blank=True)
    slug = models.SlugField()
    image = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='groups')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']

class Product(models.Model):
    """
    A model representing a product with its details, price, and inventory.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        """
        Returns a string representation of the product.
        """
        return self.title

    class Meta:
        ordering = ['title']

class ProductAttributes(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes")
    attribute = models.CharField(max_length=255)

class ProductImage(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="store/images",
        validators=[validate_file_size])

class Customer(models.Model):
    state = models.CharField(max_length=100,null=True, blank=True)
    city = models.CharField(max_length=100,null=True, blank=True)
    adress = models.CharField(max_length=300,null=True, blank=True)
    nationalid = models.CharField(max_length=10, unique=True, null=True)
    job = models.CharField(max_length=100,null=True, blank=True)
    edu = models.CharField(max_length=100,null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ('cancel_order','Can cancel order')
        ]

class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='status')
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_SENDING = 'S'
    PAYMENT_STATUS_RECEIVED = 'R'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
        (PAYMENT_STATUS_SENDING, 'Sending'),
        (PAYMENT_STATUS_RECEIVED, 'Received')
    ]
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    status_change = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart', 'product']]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

class Support(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='user')
    id = models.UUIDField(primary_key=True, default=uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    STATUS_PENDING = 'P'
    STATUS_ANSWERED = 'A'
    STATUS_COMPLETE = 'C'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ANSWERED, 'Answered'),
        (STATUS_COMPLETE, 'Complete'),
    ]
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)

class Chat(models.Model):
    support = models.ForeignKey(Support, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

class Guarantee(models.Model):
    serial = models.CharField(unique=True ,max_length=150)
    is_active = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=13, blank=True)
    created_date = models.DateField(auto_now_add=True)
    activated_date = models.DateField(null = True, blank=True)

class News(models.Model):
    title = models.CharField(default="notification", max_length=250)
    description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    writer = models.CharField(default="admin", max_length=150)
    date = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Fastcall(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=13)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)