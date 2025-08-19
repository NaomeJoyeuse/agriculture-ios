# from rest_framework import serializers
# from ..models_db.recommendation import CropRecommendation
# from ..models_db.user import User
#   # Assuming Crop model is in crop.py

# class CropRecommendationSerializer(serializers.ModelSerializer):
#     # If you want to include the user as a nested field (optional)
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

#     class Meta:
#         model = CropRecommendation
#         fields = [
#             'id', 'user', 'temperature', 'humidity', 'moisture', 'soil_type', 
#             'nitrogen', 'potassium', 'phosphorous', 'crop_predicted', 'fertilizer_predicted', 
#             'timestamp', 'status'
#         ]
    

# serializer/crop_recommendation_serializer.py

from rest_framework import serializers
from ..models_db.recommendation import CropRecommendation
from ..models_db.user import User

class CropRecommendationSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    agronomist_username = serializers.CharField(source='agronomist.username', read_only=True)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    agronomist = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    agronomist_id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CropRecommendation
        fields = [
            'id',
            'user', 'user_username',
            'agronomist', 'agronomist_username','agronomist_id',
            'status',
            # legacy numeric fields
            'temperature', 'humidity', 'moisture', 'soil_type',
            'nitrogen', 'potassium', 'phosphorous',
            'crop_predicted', 'fertilizer_predicted',
            # payloads
            'farmer_inputs', 'ai_outputs', 'fertilizer_plan',
            # agronomist writable
            'agronomist_notes', 'translated_summary',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp', 'user_username', 'agronomist_username']

    def validate(self, attrs):
        # If agronomist is set, ensure role is agronomist (if your User has role)
        agr = attrs.get('agronomist') or getattr(self.instance, 'agronomist', None)
        if agr is not None:
            role = getattr(agr, 'role', None)
            if role and str(role).lower() != 'agronomist':
                raise serializers.ValidationError({'agronomist': 'Selected user is not an agronomist'})
        return attrs

    def create(self, validated_data):
        # Prefer user from request token
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            validated_data['user'] = request.user
        # Normalize status default
        if not validated_data.get('status'):
            validated_data['status'] = 'pending_review'
        return super().create(validated_data)
    def get_agronomist_id(self, obj):
        return obj.agronomist.id if obj.agronomist else None    