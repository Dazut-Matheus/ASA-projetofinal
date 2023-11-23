from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q
from authentication.views import CustomAuthenticationPermission
from django.utils import timezone
from function.views import serializer_function
from drop.models import (
    Pedido,
    Produto,
    TipoProduto,
    StatusPedido,
)
from drop.serializer import (
    PedidoSerializer,
    TipoProdutoSerializer,
    TipoProdutoSerializer,
    StatusPedidoSerializer,
)
from users.models import Gerente, Cliente
import json
from s3image import aws_image, delete_url
from audits.views import create_audits


class ViewStatusIdentifications(viewsets.ModelViewSet):
    queryset = StatusPedido.objects.all()
    serializer_class = StatusPedidoSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        success, message, instance, http = serializer_function(
            data, StatusPedidoSerializer
        )
        return Response(
            {
                "success": success,
                "message": message,
                "data": instance,
            },
            status=http,
        )

    def get_queryset_list(self):
        queryset = super().get_queryset()
        q = Q()
        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)
        filter_id = self.request.query_params.get("id")
        if filter_id:
            q &= Q(id=filter_id)

        ordering = self.request.query_params.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)

        if self.request.query_params.get("limit") and self.request.query_params.get(
            "offset"
        ):
            filter_limit = int(self.request.query_params.get("limit"))
            filter_offset = int(self.request.query_params.get("offset"))
            queryset = queryset.filter(q)
            count = queryset.count()
            queryset = queryset[filter_offset : filter_offset + filter_limit]
        else:
            queryset = queryset.filter(q)
            count = queryset.count()

        return queryset, count

    def retrieve(self, request, *args, **kwargs):
        instance = StatusPedido.objects.filter(id=self.kwargs["pk"]).first()
        if instance:
            serializer = StatusPedidoSerializer(instance)
            return Response(
                {
                    "success": True,
                    "message": "Busca realizada com sucesso",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": True,
                "message": "Busca realizada com sucesso",
                "data": serializer.data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data["updated_at"] = timezone.now()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer.data,
        }
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset, count = self.get_queryset_list()
        queryset = self.filter_queryset(queryset)
        serializer = StatusPedidoSerializer(queryset, many=True)
        response = {
            "success": True,
            "message": "Busca realizada com sucesso",
            "total": count,
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not request.user.type == "Atumus":
            return Response(
                {
                    "success": False,
                    "message": "Apenas usuários Atumus podem realizar tal ação!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_object()
        if instance:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Status de identificações' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Status de identificações",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewTypeProducts(viewsets.ModelViewSet):
    queryset = TipoProduto.objects.all()
    serializer_class = TipoProdutoSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        success, message, instance, http = serializer_function(
            data, TipoProdutoSerializer
        )
        return Response(
            {
                "success": success,
                "message": message,
                "data": instance,
            },
            status=http,
        )

    def get_queryset_list(self):
        queryset = super().get_queryset()
        q = Q()
        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)
        filter_id = self.request.query_params.get("id")
        if filter_id:
            q &= Q(id=filter_id)

        ordering = self.request.query_params.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)

        if self.request.query_params.get("limit") and self.request.query_params.get(
            "offset"
        ):
            filter_limit = int(self.request.query_params.get("limit"))
            filter_offset = int(self.request.query_params.get("offset"))
            queryset = queryset.filter(q)
            count = queryset.count()
            queryset = queryset[filter_offset : filter_offset + filter_limit]
        else:
            queryset = queryset.filter(q)
            count = queryset.count()

        return queryset, count

    def retrieve(self, request, *args, **kwargs):
        instance = TipoProduto.objects.filter(id=self.kwargs["pk"]).first()
        if instance:
            serializer = TipoProdutoSerializer(instance)
            return Response(
                {
                    "success": True,
                    "message": "Busca realizada com sucesso",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": True,
                "message": "Busca realizada com sucesso",
                "data": serializer.data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data["updated_at"] = timezone.now()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer.data,
        }
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset, count = self.get_queryset_list()
        queryset = self.filter_queryset(queryset)
        serializer = TipoProdutoSerializer(queryset, many=True)
        response = {
            "success": True,
            "message": "Busca realizada com sucesso",
            "total": count,
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not request.user.type == "Atumus":
            return Response(
                {
                    "success": False,
                    "message": "Apenas usuários Atumus podem realizar tal ação!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_object()
        if instance:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Tipo de produto' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Tipo de produto",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewProducts(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = TipoProdutoSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"], timezone.now(), "product/" + str(data["code"])
            )
        success, message, instance, http = serializer_function(
            data, TipoProdutoSerializer
        )
        return Response(
            {
                "success": success,
                "message": message,
                "data": instance,
            },
            status=http,
        )

    def get_queryset_list(self):
        queryset = super().get_queryset()
        q = Q()
        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)
        filter_id = self.request.query_params.get("id")
        if filter_id:
            q &= Q(id=filter_id)

        ordering = self.request.query_params.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)

        if self.request.query_params.get("limit") and self.request.query_params.get(
            "offset"
        ):
            filter_limit = int(self.request.query_params.get("limit"))
            filter_offset = int(self.request.query_params.get("offset"))
            queryset = queryset.filter(q)
            count = queryset.count()
            queryset = queryset[filter_offset : filter_offset + filter_limit]
        else:
            queryset = queryset.filter(q)
            count = queryset.count()

        return queryset, count

    def retrieve(self, request, *args, **kwargs):
        instance = Produto.objects.filter(id=self.kwargs["pk"]).first()
        if instance:
            serializer = TipoProdutoSerializer(instance)
            return Response(
                {
                    "success": True,
                    "message": "Busca realizada com sucesso",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": True,
                "message": "Busca realizada com sucesso",
                "data": serializer.data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "photo" in request.data.keys():
            request.data["photo"] = aws_image(
                request.data["photo"],
                timezone.now(),
                "product/" + str(request.data["code"]),
            )
        request.data["updated_at"] = timezone.now()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer.data,
        }
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset, count = self.get_queryset_list()
        queryset = self.filter_queryset(queryset)
        serializer = TipoProdutoSerializer(queryset, many=True)
        response = {
            "success": True,
            "message": "Busca realizada com sucesso",
            "total": count,
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not request.user.type == "Atumus":
            return Response(
                {
                    "success": False,
                    "message": "Apenas usuários Atumus podem realizar tal ação!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_object()
        if instance:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Produto' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Produto",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
