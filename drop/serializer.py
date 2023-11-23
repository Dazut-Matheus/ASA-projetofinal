from rest_framework import serializers
from drop.models import Pedido, Produto, TipoProduto, StatusPedido
from users.models import Cliente, Atendende
from users.serializer import ClientsSerializer, RCAsSerializer


class TipoProdutoSerializer(serializers.ModelSerializer):
    type_product = serializers.PrimaryKeyRelatedField(
        queryset=TipoProduto.objects.all()
    )

    class Meta:
        model = Produto
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["type_product"] = TipoProdutoSerializer(
            instance.type_product
        ).data

        return representation


class TipoProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProduto
        fields = "__all__"


class PedidoSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all())
    status_identification = serializers.PrimaryKeyRelatedField(
        queryset=StatusPedido.objects.all()
    )

    class Meta:
        model = Pedido
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["client"] = ClientsSerializer(instance.client).data
        representation["product"] = TipoProdutoSerializer(instance.product).data
        representation["status_identification"] = StatusPedidoSerializer(
            instance.status_identification
        ).data
        return representation


class StatusPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusPedido
        fields = "__all__"
