from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .serializers import RegistrationSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            return Response({
                "token": token.key,
                "fullname": user.get_full_name(),
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Fehlende Felder abfangen
        errors = {}
        if email is None:
            errors["email"] = ["This field is required."]
        if password is None:
            errors["password"] = ["This field is required."]
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Django-Auth mit email als username
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"non_field_errors": ["Invalid credentials."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token":        token.key,
            "fullname":     user.get_full_name(),
            "email":        user.email,
            "user_id":      user.id
        }, status=status.HTTP_200_OK)
