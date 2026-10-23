from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        style={"input_type": "password"},
    )
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = ["date_joined"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError(
                {"password": "La contraseña es obligatoria."}
            )
        username = validated_data.pop("username", None)
        return User.objects.create_user(
            email=validated_data.pop("email"),
            password=password,
            username=username or None,
            **validated_data,
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        username = validated_data.pop("username", None)
        if username:
            instance.username = username
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
