from rest_framework import serializers
from users.models import (
    Users,
    EmailToken,
    Cliente,
    Gerente,
    Cordenador,
    Gerente,
    Supervisor,
    Atendende,
    Cidade,
)


# class PrivilegesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Privileges
#         fields = "__all__"


class EmailTokenSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())

    class Meta:
        model = EmailToken
        fields = "__all__"


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }


class AtumusSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())

    class Meta:
        model = Gerente
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UsersSerializer(instance.user).data

        return representation


class CoordinatorsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())

    class Meta:
        model = Cordenador
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UsersSerializer(instance.user).data
        return representation


class SupervisorsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    coordinator = serializers.PrimaryKeyRelatedField(queryset=Cordenador.objects.all())

    class Meta:
        model = Supervisor
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UsersSerializer(instance.user).data
        representation["coordinator"] = CoordinatorsSerializer(
            instance.coordinator
        ).data
        return representation


class RCAsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all())

    class Meta:
        model = Atendende
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UsersSerializer(instance.user).data
        representation["supervisor"] = SupervisorsSerializer(instance.supervisor).data
        return representation


class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = "__all__"


class ClientsSerializer(serializers.ModelSerializer):
    rca = serializers.PrimaryKeyRelatedField(queryset=Atendende.objects.all())
    city = serializers.PrimaryKeyRelatedField(queryset=Cidade.objects.all())

    class Meta:
        model = Cliente
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["rca"] = RCAsSerializer(instance.rca).data
        representation["city"] = CitiesSerializer(instance.city).data

        return representation
