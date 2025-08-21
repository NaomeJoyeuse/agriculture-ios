# from rest_framework import serializers
# from ..models_db.usage import Usage

# class UsageSerializer(serializers.ModelSerializer):
#     farmer_name = serializers.SerializerMethodField(read_only=True)
    
#     class Meta:
#         model = Usage
#         fields = [
#             'id', 'farmer', 'farmer_name', 'crop', 'field_name',
#             'input_type', 'product_name', 'brand',
#             'quantity', 'unit', 'cost',
#             'season_year', 'season_name', 'application_date',
#             'notes', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'farmer', 'created_at', 'updated_at']
    
#     def get_farmer_name(self, obj):
#         if hasattr(obj.farmer, 'get_full_name'):
#             name = obj.farmer.get_full_name()
#             if name:
#                 return name
#         return obj.farmer.username
    
#     def validate(self, data):
#         # Validate quantity is positive
#         if data.get('quantity', 0) <= 0:
#             raise serializers.ValidationError({"quantity": "Quantity must be greater than zero"})
        
#         # Validate cost is non-negative if provided
#         if data.get('cost') is not None and data.get('cost') < 0:
#             raise serializers.ValidationError({"cost": "Cost cannot be negative"})
        
#         # Validate unit based on input_type (optional)
#         input_type = data.get('input_type')
#         unit = data.get('unit')
#         if input_type and unit:
#             if input_type == Usage.TYPE_FERTILIZER and unit not in [Usage.UNIT_KG]:
#                 raise serializers.ValidationError({"unit": "Fertilizer should be measured in kg"})
#             elif input_type == Usage.TYPE_PESTICIDE and unit not in [Usage.UNIT_LITER]:
#                 raise serializers.ValidationError({"unit": "Pesticide should be measured in liters"})
#             elif input_type == Usage.TYPE_SEED and unit not in [Usage.UNIT_KG, Usage.UNIT_PCS]:
#                 raise serializers.ValidationError({"unit": "Seeds should be measured in kg or pieces"})
        
#         return data
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
        # Keep farmer read-only; we set it server-side
        read_only_fields = ['id', 'farmer', 'created_at', 'updated_at']

    def get_farmer_name(self, obj):
        user = getattr(obj, 'farmer', None)
        if not user:
            return None
        if hasattr(user, 'get_full_name'):
            try:
                full = user.get_full_name()
                if full:
                    return full
            except Exception:
                pass
        return getattr(user, 'username', None) or getattr(user, 'email', None) or str(user)

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        def get(key):
            return attrs.get(key, getattr(instance, key) if instance is not None else None)

        quantity = get('quantity')
        if quantity is not None and quantity <= 0:
            raise serializers.ValidationError({"quantity": "Quantity must be greater than zero"})

        cost = get('cost')
        if cost is not None and cost < 0:
            raise serializers.ValidationError({"cost": "Cost cannot be negative"})

        input_type = get('input_type')
        unit = get('unit')
        crop = get('crop')
        product_name = get('product_name')

        # Conditional requireds
        if input_type == Usage.TYPE_SEED:
            if not (crop and str(crop).strip()):
                raise serializers.ValidationError({"crop": "Crop is required for seed inputs"})
            if not (product_name and str(product_name).strip()) and crop:
                attrs['product_name'] = str(crop).strip()
        elif input_type in (Usage.TYPE_FERTILIZER, Usage.TYPE_PESTICIDE):
            if not (product_name and str(product_name).strip()):
                raise serializers.ValidationError({"product_name": "Product name is required"})

        # Unit rules
        if input_type and unit:
            if input_type == Usage.TYPE_FERTILIZER and unit != Usage.UNIT_KG:
                raise serializers.ValidationError({"unit": "Fertilizer should be measured in kg"})
            if input_type == Usage.TYPE_PESTICIDE and unit != Usage.UNIT_LITER:
                raise serializers.ValidationError({"unit": "Pesticide should be measured in liters"})
            if input_type == Usage.TYPE_SEED and unit not in (Usage.UNIT_KG, Usage.UNIT_PCS):
                raise serializers.ValidationError({"unit": "Seeds should be measured in kg or pieces"})

        return attrs

    def _uid(self):
        req = self.context.get('request')
        if not req:
            return None
        user = getattr(req, 'user', None)
        # Support your jwt_required that sets request.user_id
        return getattr(user, 'id', None) or getattr(req, 'user_id', None)

    def create(self, validated_data):
        # Always bind owner from token
        uid = self._uid()
        if not uid:
            raise serializers.ValidationError({'detail': 'Unauthenticated'})
        # Set FK via *_id to avoid fetching the user instance
        validated_data['farmer_id'] = uid
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Never allow changing owner
        validated_data.pop('farmer', None)
        validated_data.pop('farmer_id', None)
        return super().update(instance, validated_data)