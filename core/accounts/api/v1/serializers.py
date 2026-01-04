
from rest_framework.serializers import ModelSerializer,CharField,ValidationError,Serializer
from accounts.models import User,Profile
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

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

class CustomAuthTokenSerializer(Serializer):
    email = CharField(label=_("Email"), write_only=True)
    password = CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = CharField(label=_("Token"), read_only=True)
  
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )
            
            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise ValidationError(msg, code="authorization")
            if not user.is_verified:
                raise ValidationError({"details": "user is not verified"})
        else:
            msg = _('Must include "username" and "password".')
            raise ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs    
    
class ChangePasswordSerialier(Serializer):

    old_password = CharField(required=True)
    new_password = CharField(required=True)
    new_password1 = CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password1"]:
            raise ValidationError({"detail": "passwords doesnt match"})

        validate_password(attrs["new_password"], self.context["request"].user)

        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise ValidationError({"old_password": "Wrong password."})

        return super().validate(attrs)
    
    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"]) 
        user.save() 
        return user

class ProfileSerializer(ModelSerializer):
    email = CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "image",
            "description",
        )
        read_only_fields = ["email"]
