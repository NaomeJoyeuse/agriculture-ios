from rest_framework import serializers
from ..models_db.user import User
from ..models_db.feedback import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    # Write: accept PK for user
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Feedback
        fields = ["id", "user", "content", "status", "response", "created_at"]
        read_only_fields = ["id", "created_at", "status", "response"]

    def validate_content(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("Content is required")
        return v

    # Represent user as nested object on output
    def to_representation(self, instance):
        data = super().to_representation(instance)
        u = instance.user
        data["user"] = {
            "id": u.id,
            "username": getattr(u, "username", None),
            "email": getattr(u, "email", None),
            "role": getattr(u, "role", None),
        }
        return data