from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.utils import timezone
import uuid


class Users(AbstractBaseUser):
    last_login = None
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    email_verified = models.BooleanField(default=False)
    password = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=True)
    type = models.CharField(max_length=255)
    objects = UserManager()

    class Meta:
        db_table = "users"
        managed = True


class Gerente(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(Users, models.CASCADE)
    cpf = models.CharField(max_length=255, default="00000000000000")
    ds_number_phone = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    insc_estadual = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "atumus"


class Cordenador(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(Users, models.CASCADE)
    cpf = models.CharField(max_length=255, default="00000000000000")
    cnpj = models.CharField(max_length=255, default="00000000000000")
    ds_number_phone = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    insc_estadual = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "coordinators"


class Supervisor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(Users, models.CASCADE)
    coordinator = models.ForeignKey(Cordenador, models.CASCADE)
    cpf = models.CharField(max_length=255, default="00000000000000")
    ds_number_phone = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "supervisors"


class Atendende(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(Users, models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, models.CASCADE)
    cpf = models.CharField(max_length=255, default="00000000000000")
    ds_number_phone = models.CharField(max_length=255, blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "rca"


class Cidade(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    uf = models.CharField(max_length=255)

    class Meta:
        db_table = "cities"


class Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=255, blank=True, null=True)
    insc_estadual = models.CharField(max_length=255, blank=True, null=True)
    ds_number_phone = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    farm_size = models.IntegerField(blank=True, null=True)
    phone_contact_person = models.CharField(max_length=255, blank=True, null=True)
    email_contact_person = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(Cidade, models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(Users, models.CASCADE)

    class Meta:
        db_table = "clients"


class EmailToken(models.Model):
    user = models.ForeignKey(Users, models.CASCADE)
    token = models.CharField(max_length=255)

    def __str__(self):
        return str(self.token)

    class Meta:
        db_table = "email_token"
        managed = True


class PasswordResets(models.Model):
    email = models.CharField(primary_key=True, max_length=255)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.email)

    class Meta:
        db_table = "password_resets"
        managed = True
