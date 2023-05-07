from rest_framework import serializers
from django.db import transaction
from .models import *

class LikedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedItem
        fields = ['user', 'content_type', 'object_id']