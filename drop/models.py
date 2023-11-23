from django.db import models
from users.models import Cliente


class TipoProduto(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "tipo_produtos"


class Produto(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    type_product = models.ForeignKey(TipoProduto, models.CASCADE)
    photo = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "produto"


class StatusPedido(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "status_pedido"


class Pedido(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(Cliente, models.CASCADE)
    product = models.ForeignKey(Produto, models.CASCADE)
    status_identification = models.ForeignKey(StatusPedido, models.CASCADE)
    updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "pedido"


class ProdutosPedido(models.Model):
    id = models.BigAutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, models.CASCADE)
    product = models.ForeignKey(Produto, models.CASCADE)
    quantidade = models.IntegerField()
    updated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "produtos_pedido"
