import json
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import viewsets, status
from django.utils import timezone
from users.models import Users
from audits.models import AuditsRemoval
from audits.serializer import AuditsRemovalSerializer
from authentication.views import CustomAuthenticationPermission
from function.views import serializer_function


def create_audits(atumus, description, type_object, name_object, id_object):
    data_audit = {
        "atumus": atumus,
        "description": description,
        "type_object": type_object,
        "name_object": name_object,
        "id_object": id_object,
    }
    serializer_function(data_audit, AuditsRemovalSerializer)


class ViewAuditsRemoval(viewsets.ModelViewSet):
    queryset = AuditsRemoval.objects.all()
    serializer_class = AuditsRemovalSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get"]

    def get_queryset_list(self):
        queryset = super().get_queryset()
        q = Q()

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
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        response = {
            "success": True,
            "message": "Consulta executada com sucesso!",
            "data": data,
        }
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset, count = self.get_queryset_list()
        queryset = self.filter_queryset(queryset)
        serializer = AuditsRemovalSerializer(queryset, many=True)
        response = {
            "success": True,
            "message": "Busca realizada com sucesso",
            "total": count,
            "data": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
