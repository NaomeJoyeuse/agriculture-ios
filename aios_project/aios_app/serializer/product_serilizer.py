

from rest_framework import serializers
from aios_app.models_db.supplier import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'