from users.models import CustomUser
from rest_framework import serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'is_active']
        read_only= ["id"]
