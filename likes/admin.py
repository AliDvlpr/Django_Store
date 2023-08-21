from django.contrib import admin
from .models import LikedItem

# Register your models here.
@admin.register(LikedItem)
class TagAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type',
                    'object_id', 'content_object']
