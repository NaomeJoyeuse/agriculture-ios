from rest_framework import serializers
from ..models_db.farmer import Farmer
from ..models_db.user import User

class FarmerSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Farmer
        fields = [
            'id', 'user', 'user_username','fullnames',
            'phone', 'address', 'farm_size_ha', 'preferred_language', 'extra',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_username']

    def validate_user(self, user):
        role = str(getattr(user, 'role', '')).lower()
        if role and role != 'farmer':
            raise serializers.ValidationError('Selected user is not a farmer')
        return user

    def create(self, validated_data):
        # Ensure unique profile per user
        if Farmer.objects.filter(user=validated_data['user']).exists():
            raise serializers.ValidationError({'user': 'This user already has a farmer profile'})
        return super().create(validated_data)