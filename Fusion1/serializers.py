from rest_framework import serializers
from .models import FontModel  # Import your model

class FontModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FontModel
        fields = '__all__'  # You can specify fields you want to include