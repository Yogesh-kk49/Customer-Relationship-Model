from django.contrib.auth.models import settings
User = settings.AUTH_USER_MODEL
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
