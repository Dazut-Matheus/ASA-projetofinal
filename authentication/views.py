from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        return validated_data


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


custom_token_refresh_view = CustomTokenRefreshView.as_view()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        attrs[self.username_field] = attrs["email"]
        return super().validate(attrs)


def generate_tokens_for_user(email, password):
    data = {"email": email, "password": password}
    serializer = CustomTokenObtainPairSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    refresh_token = RefreshToken(serializer.validated_data["refresh"])
    access_token = str(refresh_token.access_token)
    return {"access": access_token, "refresh": str(refresh_token)}


class CustomAuthenticationPermission(permissions.BasePermission):
    authentication_classes = [JWTAuthentication]

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "message": "Usuário não autenticado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return True
