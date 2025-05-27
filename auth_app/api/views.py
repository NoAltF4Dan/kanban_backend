from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError

from .serializers import RegistrationSerializer


class RegisterView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "fullname": user.get_full_name(),
                    "email": user.email,
                    "user_id": user.id
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        errors = {}
        if not email:
            errors["email"] = ["This field is required."]
        if not password:
            errors["password"] = ["This field is required."]
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({"non_field_errors": ["Invalid credentials."]}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "fullname": user.get_full_name(),
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_200_OK)
