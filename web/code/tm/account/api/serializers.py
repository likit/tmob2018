from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Profile

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name_th', 'last_name_th', 'current_affiliation', 'current_position', 'about', 'field_of_interest']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'profile']
