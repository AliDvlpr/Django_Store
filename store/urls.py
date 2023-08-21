from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views
from likes.views import LikedItemViewSet
from images.views import ImageViewSet

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('groups', views.GroupViewSet, basename='groups')
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('support', views.SupportViewSet)
router.register('fastcall', views.FastcallViewSet, basename='fastcall')
router.register('guarantee', views.GuaranteeViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
router.register('mainpage', views.MainPageViewSet)
router.register('news', views.NewsViewSet)
router.register('likes', LikedItemViewSet, basename='likes')
router.register('images', ImageViewSet, basename='images')
router.register('notifications', views.NotificationsViewSet, basename='notifications')

support_router = routers.NestedDefaultRouter(router, 'support', lookup='support')
support_router.register('chat', views.ChatViewSet, basename='support-chats')


products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet,
                         basename='product-reviews')
products_router.register('images', views.ProductImageViewSet,
                         basename='product-images')
products_router.register('attributes', views.ProductAttributesViewSet,
                         basename='product-attributes')
products_router.register('powers', views.ProductPowersViewSet,
                         basename='product-powers')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

orders_router = routers.NestedDefaultRouter(router, 'orders', lookup='order')
orders_router.register('status', views.OrderStatusViewSet, basename='order-status')

# URLConf
urlpatterns = router.urls + products_router.urls + carts_router.urls + orders_router.urls + support_router.urls
