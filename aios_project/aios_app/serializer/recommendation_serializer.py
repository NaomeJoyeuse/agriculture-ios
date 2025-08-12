from rest_framework import serializers
from ..models_db.recommendation import CropRecommendation
from ..models_db.user import User
  # Assuming Crop model is in crop.py

class CropRecommendationSerializer(serializers.ModelSerializer):
    # If you want to include the user as a nested field (optional)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = CropRecommendation
        fields = [
            'id', 'user', 'temperature', 'humidity', 'moisture', 'soil_type', 
            'nitrogen', 'potassium', 'phosphorous', 'crop_predicted', 'fertilizer_predicted', 
            'timestamp', 'status'
        ]
    