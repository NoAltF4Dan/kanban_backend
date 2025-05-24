from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("fullname", "email", "password", "repeated_password")

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        full_name = validated_data.pop("fullname")
        validated_data.pop("repeated_password")

        email = validated_data["email"]
        password = validated_data["password"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = full_name
        user.save()

        Token.objects.create(user=user)
        return user