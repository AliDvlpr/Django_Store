from datetime import timedelta
from django.utils import timezone
from .models import Cart, CartItem

def clean_expired_carts():
    # Delete carts without items that are older than 3 days
    three_days_ago = timezone.now() - timedelta(days=3)
    carts_to_delete = Cart.objects.filter(items__isnull=True, created_at__lt=three_days_ago)
    carts_to_delete.delete()

def clean_old_carts():
    # Delete carts older than 20 days
    twenty_days_ago = timezone.now() - timedelta(days=20)
    old_carts_to_delete = Cart.objects.filter(created_at__lt=twenty_days_ago)
    old_carts_to_delete.delete()
