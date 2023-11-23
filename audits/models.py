from django.db import models
from users.models import Gerente


class AuditsRemoval(models.Model):
    id = models.BigAutoField(primary_key=True)
    atumus = models.BigIntegerField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type_object = models.CharField(max_length=255, blank=True, null=True)
    name_object = models.CharField(max_length=255, blank=True, null=True)
    id_object = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "audits_removal"
