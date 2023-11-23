import json
from django.http import JsonResponse
from rest_framework import viewsets
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.urls import resolve
from django.utils import timezone
from function.views import serializer_function, date_format
from s3image import get_url


class DateTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(response)

    def process_response(self, response):
        if hasattr(response, "data"):
            self.process_data(response.data)
            response.content = json.dumps(response.data, default=self.process_datetime)
            response["Content-Type"] = "application/json"
        return response

    def process_data(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                field_list_date = [
                    "created_at",
                    "updated_at",
                    "paid_at",
                    "date_reference_at",
                    "date_initial",
                    "date_final",
                ]
                field_list_photo = [
                    "photo",
                    "photo_before_without_product",
                    "photo_before_with_product",
                    "photo_after_without_product",
                    "photo_after_with_product",
                ]
                if isinstance(value, dict):
                    self.process_data(value)
                elif isinstance(value, list):
                    self.process_list(value)
                elif key in field_list_date:
                    data[key] = self.process_datetime(value)
                elif key in field_list_photo:
                    data[key] = self.process_url_photo(value)

    def process_list(self, data_list):
        for item in data_list:
            self.process_data(item)

    def process_datetime(self, value):
        return date_format(value)

    def process_url_photo(self, value):
        return get_url(value)


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, kwargs):
        # Verificar as permissões apenas para as subclasses de ViewSets
        if hasattr(view_func, "cls") and issubclass(
            view_func.cls, viewsets.ModelViewSet
        ):
            user = request.user
            action = kwargs.get("pk") and "retrieve" or kwargs.get("action")
            if not self.has_permission(user, action):
                raise PermissionDenied("Permissão negada.")

    def has_permission(self, user, action):
        # Verificar se o usuário tem a permissão para a ação
        # Usar a tabela auth_permission e as tabelas relacionais para verificar as permissões
        # Retornar True se o usuário tiver permissão ou False caso contrário

        # Obtém o codinome da permissão com base na ação da view
        codename = self.get_permission_codename(action)

        # Verifica se o usuário tem a permissão
        if user.has_perm(codename):
            return True

        # Se o usuário não tiver a permissão específica,
        # verifique se o usuário tem permissão através de grupos
        if user.groups.exists():
            permissions = Permission.objects.filter(group__user=user, codename=codename)
            if permissions.exists():
                return True

        # return False
        return True

    def get_permission_codename(self, action):
        # Mapeia a ação da view para o codinome da permissão correspondente
        if action == "list":
            return "view"
        elif action == "retrieve":
            return "view"
        elif action == "create":
            return "add"
        elif action == "update":
            return "change"
        elif action == "partial_update":
            return "change"
        elif action == "destroy":
            return "delete"
        else:
            return ""
