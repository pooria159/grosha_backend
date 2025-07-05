from rest_framework import serializers
from sellers.models import Seller
from sellers.serializers import SellerSerializer
from django.contrib.auth import get_user_model

from team_management.models import StoreRole

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class StoreRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    
    class Meta:
        model = StoreRole
        fields = ['id', 'user', 'seller', 'role', 'is_active', 'created_at']

class CreateStoreRoleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = StoreRole
        fields = ['user', 'role']

class ToggleActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()