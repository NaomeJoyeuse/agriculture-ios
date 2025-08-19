from rest_framework import serializers
from ..models_db.usage import Usage

class UsageSerializer(serializers.ModelSerializer):
    farmer_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Usage
        fields = [
            'id', 'farmer', 'farmer_name', 'crop', 'field_name',
            'input_type', 'product_name', 'brand',
            'quantity', 'unit', 'cost',
            'season_year', 'season_name', 'application_date',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'farmer', 'created_at', 'updated_at']
    
    def get_farmer_name(self, obj):
        if hasattr(obj.farmer, 'get_full_name'):
            name = obj.farmer.get_full_name()
            if name:
                return name
        return obj.farmer.username
    
    def validate(self, data):
        # Validate quantity is positive
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError({"quantity": "Quantity must be greater than zero"})
        
        # Validate cost is non-negative if provided
        if data.get('cost') is not None and data.get('cost') < 0:
            raise serializers.ValidationError({"cost": "Cost cannot be negative"})
        
        # Validate unit based on input_type (optional)
        input_type = data.get('input_type')
        unit = data.get('unit')
        if input_type and unit:
            if input_type == Usage.TYPE_FERTILIZER and unit not in [Usage.UNIT_KG]:
                raise serializers.ValidationError({"unit": "Fertilizer should be measured in kg"})
            elif input_type == Usage.TYPE_PESTICIDE and unit not in [Usage.UNIT_LITER]:
                raise serializers.ValidationError({"unit": "Pesticide should be measured in liters"})
            elif input_type == Usage.TYPE_SEED and unit not in [Usage.UNIT_KG, Usage.UNIT_PCS]:
                raise serializers.ValidationError({"unit": "Seeds should be measured in kg or pieces"})
        
        return data