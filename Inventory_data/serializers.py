from rest_framework import serializers
from .models import InventoryItem
from django.contrib.auth.models import User

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self,validate_data):
        user = User.objects.create_user(username=validate_data['username'],
                                    password = validate_data['password'])
        return user
