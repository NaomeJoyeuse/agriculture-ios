from rest_framework import serializers
from aios_app.models_db.input_usage import InputUsage

class InputUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputUsage
        fields = '__all__'
