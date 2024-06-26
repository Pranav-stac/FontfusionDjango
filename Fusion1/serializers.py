from rest_framework import serializers
from .models import FontModel  # Import your model


from django.contrib.auth.models import User
from rest_framework import serializers

from .models import FontModel, UserProfile  # Import your models

class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, source='profile.role', write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role_data = validated_data.pop('profile', {}).get('role')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, role=role_data)
        return user
class FontModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FontModel
        fields = '__all__'  # You can specify fields you want to include