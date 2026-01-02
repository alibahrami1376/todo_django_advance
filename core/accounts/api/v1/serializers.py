
from rest_framework.serializers import ModelSerializer,CharField,ValidationError
from accounts.models import User
from django.contrib.auth.password_validation import validate_password

class RegistrationSerializer(ModelSerializer):
    password1 = CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password1"]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password1"):
            raise ValidationError({"detail": "passswords doesnt match"})

        try:
            validate_password(attrs.get("password"))
        except ValidationError as e:
            raise ValidationError({"password": list(e.messages)})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)
