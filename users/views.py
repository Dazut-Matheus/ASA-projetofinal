import datetime, json, random, pytz
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from users.models import (
    Users,
    PasswordResets,
    EmailToken,
    Cliente,
    Cordenador,
    Gerente,
    Supervisor,
    Atendende,
    Cidade,
)
from users.serializer import (
    UsersSerializer,
    EmailTokenSerializer,
    CoordinatorsSerializer,
    ClientsSerializer,
    AtumusSerializer,
    SupervisorsSerializer,
    RCAsSerializer,
    CitiesSerializer,
)
from django.contrib.auth import logout
from django.db.models import Q
from authentication.views import (
    CustomAuthenticationPermission,
    generate_tokens_for_user,
)
from rest_framework.pagination import LimitOffsetPagination
from django.utils import timezone
from function.views import (
    serializer_function,
    delete_objects,
    envia_email,
)
from s3image import get_url, aws_image
import random
from audits.views import create_audits


class ViewLogin(APIView):
    permission_classes = []
    http_method_names = ["post"]

    def login_user(self, request):
        data = json.loads(request.body)
        if "email" not in data.keys() or "password" not in data.keys():
            return Response(
                {"message": "Falta de preenchimento de campo obrigatório"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        email = data["email"]
        password = data["password"]

        instance = Users.objects.filter(email=email).first()
        if instance:
            che = check_password(password=password, encoded=instance.password)
            if not instance.is_approved or not instance.is_active:
                return Response(
                    {"success": False, "message": "Usuário inativo"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if che:
                tokens = generate_tokens_for_user(email, password)
                perfil = None
                if instance.type == "Atumus":
                    instance_perfil = Gerente.objects.filter(
                        user__id=instance.id
                    ).first()
                    perfil = AtumusSerializer(instance_perfil).data
                if instance.type == "Coordinators":
                    instance_perfil = Cordenador.objects.filter(
                        user__id=instance.id
                    ).first()
                    perfil = CoordinatorsSerializer(instance_perfil).data
                if instance.type == "Supervisors":
                    instance_perfil = Supervisor.objects.filter(
                        user__id=instance.id
                    ).first()
                    perfil = SupervisorsSerializer(instance_perfil).data
                if instance.type == "RCAs":
                    instance_perfil = Atendende.objects.filter(
                        user__id=instance.id
                    ).first()
                    perfil = RCAsSerializer(instance_perfil).data
                response = {
                    "success": True,
                    "message": "Sucesso ao realizar a autenticação.",
                    "user": perfil,
                    "tokens": {
                        "access_token": tokens["access"],
                        "refresh_token": tokens["refresh"],
                    },
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"success": False, "message": "Credenciais inválidas"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(
                {"success": False, "message": "Usuário não encontrado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def forgotten(self, request):
        if request.method == "POST":
            data = json.loads(request.body)
            if "email" not in data.keys():
                return Response(
                    {"message": "Falta de preenchimento de campo obrigatório"},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )
        else:
            return Response(
                {"success": False, "message": "Método inválido!"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        person = Users.objects.filter(email=data["email"]).first()
        if person:
            hash = str(random.random())[5:11]
            instance = PasswordResets.objects.filter(email=person.email)
            if instance:
                instance.delete()
            created_at = datetime.datetime.now()
            text_body = "Seu código de recuperação é: " + hash
            send = envia_email(person.email, "Recuperação de senha", text_body)
            if not send:
                return Response(
                    {"success": False, "message": "Falha ao enviar email!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            json_ = {"token": hash, "created_at": created_at, "email": person.email}
            S = PasswordResets(**json_)
            S.save()
            return Response(
                {"success": True, "message": "E-mail enviado com sucesso!"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "message": "Usuario não encontrado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def reset_password(self, request):
        # Checagem do método request. Atribuição do body a variáveis utilizadas
        if request.method == "POST":
            data = json.loads(request.body)
            if (
                "email" not in data.keys()
                or "token" not in data.keys()
                or "password" not in data.keys()
                or "password_confirmation" not in data.keys()
            ):
                return Response(
                    {"message": "Falta de preenchimento de campo obrigatório"},
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )
            email = data["email"]
            token = data["token"]
            password = data["password"]
            password_confirmation = data["password_confirmation"]
        else:
            return Response(
                {"message": "Método enviado não é um post"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        # Filtragem do pedido para recuperação de senha de acordo com o email
        reset_person = PasswordResets.objects.filter(email=email).first()
        if reset_person:
            # Checagem se o token enviado pelo usuário corresponde ao gerado pelo sistema
            if reset_person.token == token:
                # Checagem se o token ainda é válido de acordo com tempo de expiração
                agora = datetime.datetime.now(tz=pytz.utc)
                expired = agora >= reset_person.created_at + datetime.timedelta(hours=8)

                if expired:
                    return Response(
                        {"success": False, "message": "Token expirado!"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                else:
                    # Checagem se a senha e sua confirmação correspondem
                    if password == password_confirmation:
                        # Filtragem do usuário de acordo com o email
                        instance = Users.objects.filter(
                            email=email, is_approved=True
                        ).first()
                        # Checando se o usuário existe
                        if instance:
                            # Codificação da nova senha e atribuição ao usuário
                            instance.password = make_password(
                                password=data["password"],
                                salt=None,
                                hasher="pbkdf2_sha256",
                            )
                            # Salvando novos dados do usuário
                            instance.save()
                            # Deletando instância do pedido de mudança de senha do PasswordResets
                            reset_person.delete()
                            return Response(
                                {
                                    "success": True,
                                    "message": "Senha trocada com sucesso!",
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            return Response(
                                {"success": False, "message": "Usuário não existe"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    else:
                        return Response(
                            {"success": False, "message": "As senhas não coincidem"},
                            status=status.HTTP_428_PRECONDITION_REQUIRED,
                        )
            else:
                response = {
                    "success": False,
                    "message": "Verifique se as informações foram inseridas corretamente",
                    "data": {"errors": {"token": ["The selected token is invalid."]}},
                }

                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(
            {"success": False, "message": "Usuario não encontrado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def refresh(self, request):
        # Checagem do método da requisição
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                if "refresh_token" not in data.keys():
                    return Response(
                        {"message": "Falta de token"},
                        status=status.HTTP_412_PRECONDITION_FAILED,
                    )

            except json.JSONDecodeError as e:
                return Response(
                    {
                        "message": "Erro ao decodificar o corpo da requisição: {}".format(
                            str(e)
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                refresh = RefreshToken(data["refresh_token"])
            except Exception as e:
                return Response(
                    {"success": False, "message": "Sessão expiradas"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                access_token = str(refresh.access_token)
            except Exception as e:
                return Response(
                    {"message": "Erro ao obter o novo token de acesso"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Sucesso
            response_data = {
                "success": True,
                "message": "Tokens atualizados com sucesso",
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": data["refresh_token"],
                },
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            return Response(
                {"message": "Método enviado não é um post"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

    def check_hash(self, request):
        # Atribuição do body ao dicionário data
        data = json.loads(request.body)
        if not "token" in data.keys() or not "email" in data.keys():
            return Response(
                {"success": False, "message": "Falta de token"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        token = data["token"]
        email = data["email"]

        instance = PasswordResets.objects.filter(token=token, email=email).first()
        if instance:
            return Response(
                {"success": True, "message": "Token válido"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "message": "Token inválido"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def post(self, request, action):
        if action == "login":
            return self.login_user(request)
        elif action == "forgotten":
            return self.forgotten(request)
        elif action == "reset":
            return self.reset_password(request)
        elif action == "refresh":
            return self.refresh(request)
        elif action == "check":
            return self.check_hash(request)
        else:
            return Response(
                {"success": False, "message": "Ação inválida"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ViewProfile(APIView):
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch"]

    def patch(self, request):
        data = json.loads(request.body)
        instance = Users.objects.filter(id=request.user.id).first()

        if instance.type == "Atumus":
            model = Gerente
            serializer = AtumusSerializer
        if instance.type == "Coordinators":
            model = Cordenador
            serializer = CoordinatorsSerializer
        if instance.type == "Supervisors":
            model = Supervisor
            serializer = SupervisorsSerializer
        if instance.type == "RCAs":
            model = Atendende
            serializer = RCAsSerializer

        data["updated_at"] = timezone.now()
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"],
                timezone.now(),
                "clients/profile" + str(instance_perfil.id),
            )
        if "password" in data.keys():
            instance.password = make_password(
                password=data["password"], salt=None, hasher="pbkdf2_sha256"
            )
            instance.save()
        if "email" in data.keys():
            instance.email = data["email"]
            instance.save()

        instance_perfil = model.objects.filter(user__id=instance.id).first()
        serializer_data = serializer(instance_perfil, data=data, partial=True)
        serializer_data.is_valid(raise_exception=True)

        serializer_data.save()
        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer_data.data,
        }
        return Response(response)

    def get(self, request):
        instance = Users.objects.filter(id=request.user.id).first()
        if instance.type == "Atumus":
            model = Gerente
            serializer = AtumusSerializer
        if instance.type == "Coordinators":
            model = Cordenador
            serializer = CoordinatorsSerializer
        if instance.type == "Supervisors":
            model = Supervisor
            serializer = SupervisorsSerializer
        if instance.type == "RCAs":
            model = Atendende
            serializer = RCAsSerializer

        instance_client = model.objects.filter(user=request.user.id).first()
        serializer_data = serializer(instance_client)
        response = {
            "success": True,
            "message": "Busca realizada com sucesso",
            "data": serializer_data.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class ViewEmailVerify(APIView):
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "post"]

    def post(self, request):
        instance = Users.objects.filter(id=request.user.id).first()
        instance_email_token = EmailToken.objects.get(
            token=request.data["token"], user__id=request.user.id
        )
        instance.updated_at = timezone.now()
        instance.email_verified = True
        instance.save()
        instance_email_token.delete()
        serializer = UsersSerializer(instance)
        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer.data,
        }
        return Response(response)

    def get(self, request):
        if request.user.email_verified:
            return Response(
                {"success": False, "message": "Este email já está verificado!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        old_tokens = EmailToken.objects.filter(user=request.user.id)
        delete_objects(old_tokens)
        token = str(random.random())[5:11]
        data = {"user": request.user.id, "token": token}
        success, message, instance, http = serializer_function(
            data, EmailTokenSerializer
        )
        text_body = "Seu código de ativação é: " + token
        send = envia_email(request.user.email, "Ativação de email", text_body)
        if not send:
            return JsonResponse(
                {"success": False, "message": "Falha ao enviar email!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"success": success, "message": "Código enviado ao seu email"},
            status=http,
        )


class ViewUsers(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "delete"]

    # def create(self, request, *args, **kwargs):
    #     data = json.loads(request.body)
    #     data["password"] = make_password(
    #         password=data["password"], salt=None, hasher="pbkdf2_sha256"
    #     )
    #     success, message, instance, http = serializer_function(data, UsersSerializer)
    #     return Response(
    #         {
    #             "success": success,
    #             "message": message,
    #             "data": instance,
    #         },
    #         status=http,
    #     )

    def get_queryset_list(self):
        queryset = super().get_queryset()
        q = Q()

        filter_name = self.request.query_params.get("name")
        if filter_name:
            q &= Q(name__icontains=filter_name)

        filter_email = self.request.query_params.get("email")
        if filter_email:
            q &= Q(email__icontains=filter_email)

        filter_is_approved = self.request.query_params.get("is_approved")
        if filter_is_approved:
            q &= Q(is_approved=filter_is_approved)
        filter_is_active = self.request.query_params.get("is_active")
        if filter_is_active:
            q &= Q(is_active=filter_is_active)

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
        if not request.user.type == "Atumus":
            return Response(
                {
                    "success": False,
                    "message": "Apenas usuários Atumus podem realizar tal ação!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        response = {
            "success": True,
            "message": "Consulta executada com sucesso!",
            "data": data,
        }
        return Response(response)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.type == "Atumus":
            return Response(
                {
                    "success": False,
                    "message": "Apenas usuários Atumus podem realizar tal ação!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = json.loads(request.body)
        instance = self.get_object()
        if instance.type == "Atumus":
            model = Gerente
            serializer = AtumusSerializer
        if instance.type == "Coordinators":
            model = Cordenador
            serializer = CoordinatorsSerializer
        if instance.type == "Supervisors":
            model = Supervisor
            serializer = SupervisorsSerializer
        if instance.type == "RCAs":
            model = Atendende
            serializer = RCAsSerializer
        if "password" in data.keys():
            instance.password = make_password(
                password=data["password"], salt=None, hasher="pbkdf2_sha256"
            )
            instance.save()
        if "email" in data.keys():
            instance.email = data["email"]
            instance.save()
        request.data["updated_at"] = timezone.now()

        instance_perfil = model.objects.filter(user__id=instance.id).first()
        serializer_data = serializer(instance_perfil, data=data, partial=True)
        serializer_data.is_valid(raise_exception=True)

        serializer_data.save()
        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer_data.data,
        }
        return Response(response)

    def list(self, request, *args, **kwargs):
        if not request.user.type == "Atumus":
            return Response(
                {
                    "success": False,
                    "message": "Apenas usuários Atumus podem realizar tal ação!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset, count = self.get_queryset_list()
        queryset = self.filter_queryset(queryset)
        serializer = UsersSerializer(queryset, many=True)
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
                + "' deletou um(a) 'Usuário' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Usuário",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewAtumus(viewsets.ModelViewSet):
    queryset = Gerente.objects.all()
    serializer_class = AtumusSerializer
    permission_classes = [CustomAuthenticationPermission]
    # Comentada para teste
    # authentication_classes = []
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data["password"] == "":
            data["password"] = str(random.random())[2:11]
        temp_password = data["password"]
        data["password"] = make_password(
            password=data["password"], salt=None, hasher="pbkdf2_sha256"
        )
        data["type"] = "Atumus"
        success_user, message_user, instance_user, http_user = serializer_function(
            data, UsersSerializer
        )
        if not success_user:
            return Response(
                {
                    "success": success_user,
                    "message": message_user,
                    "data": http_user,
                },
                status=http,
            )
        data["user"] = instance_user["id"]
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"], timezone.now(), "Atumus/profile" + str(instance.id)
            )
        success, message, instance, http = serializer_function(data, AtumusSerializer)
        if not success:
            delete_objects(Users.objects.filter(id=instance_user["id"]))
        else:
            text_body = "Sua senha de acesso é: " + temp_password
            envia_email(data["email"], "Senha de acesso", text_body)
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
        if not self.request.user.type == "Atumus":
            return queryset.none()
        filter_name = self.request.query_params.get("name")
        if filter_name:
            q &= Q(name__icontains=filter_name)

        filter_email = self.request.query_params.get("email")
        if filter_email:
            q &= Q(email__icontains=filter_email)

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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "email" in request.data.keys():
            instance_user = Users.objects.filter(id=instance.user_id).first()
            instance_user.email = request.data["email"]
            instance_user.save()
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
        serializer = AtumusSerializer(queryset, many=True)
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
        instance_user = instance.user
        if instance_user:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'usuário atumus' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Atumus",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewCoordinators(viewsets.ModelViewSet):
    queryset = Cordenador.objects.all()
    serializer_class = CoordinatorsSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data["password"] == "":
            data["password"] = str(random.random())[2:11]
        temp_password = data["password"]
        data["password"] = make_password(
            password=data["password"], salt=None, hasher="pbkdf2_sha256"
        )
        data["type"] = "Coordinators"
        success_user, message_user, instance_user, http_user = serializer_function(
            data, UsersSerializer
        )
        if not success_user:
            return Response(
                {
                    "success": success_user,
                    "message": message_user,
                    "data": http_user,
                },
                status=http,
            )
        data["user"] = instance_user["id"]
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"], timezone.now(), "coordinators/profile" + str(instance.id)
            )
        success, message, instance, http = serializer_function(
            data, CoordinatorsSerializer
        )
        if not success:
            delete_objects(Users.objects.filter(id=instance_user["id"]))
        else:
            text_body = "Sua senha de acesso é: " + temp_password
            envia_email(data["email"], "Senha de acesso", text_body)
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
        if self.request.user.type == "Coordinators":
            q &= Q(user__id=self.request.user.id)
        elif not self.request.user.type == "Atumus":
            return queryset.none()

        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)
        filter_name = self.request.query_params.get("name")
        if filter_name:
            q &= Q(name__icontains=filter_name)

        filter_email = self.request.query_params.get("email")
        if filter_email:
            q &= Q(email__icontains=filter_email)

        filter_is_approved = self.request.query_params.get("is_approved")
        if filter_is_approved:
            q &= Q(is_approved=filter_is_approved)
        filter_is_active = self.request.query_params.get("is_active")
        if filter_is_active:
            q &= Q(is_active=filter_is_active)

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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "email" in request.data.keys():
            instance_user = Users.objects.filter(id=instance.user_id).first()
            instance_user.email = request.data["email"]
            instance_user.save()
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
        serializer = CoordinatorsSerializer(queryset, many=True)
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
        instance_user = instance.user
        if instance_user:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Coordenador' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Coordenador",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewSupervisors(viewsets.ModelViewSet):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorsSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data["password"] == "":
            data["password"] = str(random.random())[2:11]
        temp_password = data["password"]
        data["password"] = make_password(
            password=data["password"], salt=None, hasher="pbkdf2_sha256"
        )
        data["type"] = "Supervisors"
        success_user, message_user, instance_user, http_user = serializer_function(
            data, UsersSerializer
        )
        if not success_user:
            return Response(
                {
                    "success": success_user,
                    "message": message_user,
                    "data": http_user,
                },
                status=http,
            )
        data["user"] = instance_user["id"]
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"], timezone.now(), "Supervisors/profile" + str(instance.id)
            )
        success, message, instance, http = serializer_function(
            data, SupervisorsSerializer
        )
        if not success:
            delete_objects(Users.objects.filter(id=instance_user["id"]))
        else:
            text_body = "Sua senha de acesso é: " + temp_password
            envia_email(data["email"], "Senha de acesso", text_body)
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

        if self.request.user.type == "Supervisors":
            q &= Q(user__id=self.request.user.id)
        elif self.request.user.type == "Coordinators":
            q &= Q(coordinator__user__id=self.request.user.id)
        elif self.request.user.type == "Atumus":
            pass
        else:
            return queryset.none()

        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)

        filter_name = self.request.query_params.get("name")
        if filter_name:
            q &= Q(name__icontains=filter_name)

        filter_email = self.request.query_params.get("email")
        if filter_email:
            q &= Q(email__icontains=filter_email)

        filter_is_approved = self.request.query_params.get("is_approved")
        if filter_is_approved:
            q &= Q(is_approved=filter_is_approved)
        filter_is_active = self.request.query_params.get("is_active")
        if filter_is_active:
            q &= Q(is_active=filter_is_active)

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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "email" in request.data.keys():
            instance_user = Users.objects.filter(id=instance.user_id).first()
            instance_user.email = request.data["email"]
            instance_user.save()
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
        serializer = SupervisorsSerializer(queryset, many=True)
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
        instance_user = instance.user
        if instance_user:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Supervisor' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Supervisor",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewRCAs(viewsets.ModelViewSet):
    queryset = Atendende.objects.all()
    serializer_class = RCAsSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if data["password"] == "":
            data["password"] = str(random.random())[2:11]
        temp_password = data["password"]
        data["password"] = make_password(
            password=data["password"], salt=None, hasher="pbkdf2_sha256"
        )
        data["type"] = "RCAs"
        success_user, message_user, instance_user, http_user = serializer_function(
            data, UsersSerializer
        )
        if not success_user:
            return Response(
                {
                    "success": success_user,
                    "message": message_user,
                    "data": instance_user,
                },
                status=http_user,
            )
        data["user"] = instance_user["id"]
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"], timezone.now(), "RCAs/profile" + str(instance.id)
            )
        success, message, instance, http = serializer_function(data, RCAsSerializer)
        if not success:
            delete_objects(Users.objects.filter(id=instance_user["id"]))
        else:
            text_body = "Sua senha de acesso é: " + temp_password
            envia_email(data["email"], "Senha de acesso", text_body)
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
        if self.request.user.type == "RCAs":
            q &= Q(user__id=self.request.user.id)
        elif self.request.user.type == "Supervisors":
            q &= Q(supervisor__user__id=self.request.user.id)
        elif self.request.user.type == "Coordinators":
            q &= Q(supervisor__coordinator__user__id=self.request.user.id)
        elif self.request.user.type == "Atumus":
            pass
        else:
            return queryset.none()

        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)

        filter_name = self.request.query_params.get("name")
        if filter_name:
            q &= Q(name__icontains=filter_name)

        filter_email = self.request.query_params.get("email")
        if filter_email:
            q &= Q(email__icontains=filter_email)

        filter_is_approved = self.request.query_params.get("is_approved")
        if filter_is_approved:
            q &= Q(is_approved=filter_is_approved)
        filter_is_active = self.request.query_params.get("is_active")
        if filter_is_active:
            q &= Q(is_active=filter_is_active)

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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # print()
        # if not request.user.type == "Atumus" and "is_active" in request.data.keys():
        #     request.data.pop("is_active")
        if "email" in request.data.keys():
            instance_user = Users.objects.filter(id=instance.user_id).first()
            instance_user.email = request.data["email"]
            instance_user.save()
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
        serializer = RCAsSerializer(queryset, many=True)
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
        instance_user = instance.user
        if instance_user:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Representante' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Representante",
                instance.name,
                instance.id,
            )
            instance.delete()

            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewClients(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClientsSerializer
    # permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)

        data["type"] = "clients"
        if "photo" in data.keys():
            data["photo"] = aws_image(
                data["photo"], timezone.now(), "clients/profile" + str(instance.id)
            )
        success, message, instance, http = serializer_function(data, ClientsSerializer)
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
        if self.request.user.type == "RCAs":
            q &= Q(rca__user__id=self.request.user.id)
        if self.request.user.type == "Supervisors":
            q &= Q(rca__supervisor__user__id=self.request.user.id)
        if self.request.user.type == "Coordinators":
            q &= Q(rca__supervisor__coordinator__user__id=self.request.user.id)

        filter_active = self.request.query_params.get("is_active")
        if filter_active:
            q &= Q(is_active=filter_active)
        if not filter_active:
            q &= Q(is_active=True)

        filter_rca = self.request.query_params.get("rca")
        if filter_rca:
            q &= Q(rca__id=filter_rca)

        filter_name = self.request.query_params.get("name")
        if filter_name:
            q &= Q(name__icontains=filter_name)

        filter_email = self.request.query_params.get("email")
        if filter_email:
            q &= Q(email__icontains=filter_email)

        filter_is_approved = self.request.query_params.get("is_approved")
        if filter_is_approved:
            q &= Q(is_approved=filter_is_approved)
        filter_is_active = self.request.query_params.get("is_active")
        if filter_is_active:
            q &= Q(is_active=filter_is_active)

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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "rca" in request.data.keys():
            old_rca = Atendende.objects.filter(id=instance.rca.id).first()
            new_rca = Atendende.objects.filter(id=request.data["rca"]).first()
        if not request.user.type == "Atumus" and "is_active" in request.data.keys():
            request.data.pop("is_active")
        if "photo" in request.data.keys():
            request.data["photo"] = aws_image(
                request.data["photo"],
                timezone.now(),
                "product/" + str(request.data["code"]),
            )
        if not request.user.type == "Atumus":
            data = {}
            if "email" in request.data.keys():
                data["email"] = request.data["email"]
            if "ds_number_phone" in request.data.keys():
                data["ds_number_phone"] = request.data["ds_number_phone"]
            if "farm_size" in request.data.keys():
                data["farm_size"] = request.data["farm_size"]
            if "neighborhood" in request.data.keys():
                data["neighborhood"] = request.data["neighborhood"]
            if "city" in request.data.keys():
                data["city"] = request.data["city"]
            if "state" in request.data.keys():
                data["state"] = request.data["state"]
            if "zip_code" in request.data.keys():
                data["zip_code"] = request.data["zip_code"]
        else:
            data = request.data
        data["updated_at"] = timezone.now()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "rca" in request.data.keys():
            atumus = Gerente.objects.filter(user__id=request.user.id).first()
            data_history = {
                "rca_added": new_rca.id,
                "rca_removed": old_rca.id,
                "atumus": atumus.id,
                "client": instance.id,
                "message": "O cliente '"
                + instance.name
                + "' foi movido do representante: '"
                + old_rca.name
                + "' para o representante : '"
                + new_rca.name
                + "' por: '"
                + atumus.name
                + "'",
            }

        response = {
            "success": True,
            "message": "Modificado com sucesso!",
            "data": serializer.data,
        }
        return Response(response)

    def list(self, request, *args, **kwargs):
        queryset, count = self.get_queryset_list()
        queryset = self.filter_queryset(queryset)
        serializer = ClientsSerializer(queryset, many=True)
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

        atumus = Gerente.objects.filter(user__id=request.user.id).first()
        data_history = {
            "rca_removed": instance.rca.id,
            "atumus": atumus.id,
            "client": instance.id,
            "message": "O cliente '"
            + instance.name
            + "' foi deletado do representante: '"
            + instance.rca.name
            + "' por: '"
            + atumus.name
            + "'",
        }

        if instance:
            atumus = Gerente.objects.filter(user_id=request.user.id).first()
            description = (
                "O usuário atumus '"
                + atumus.name
                + "' deletou um(a) 'Cliente' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Cliente",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ViewCities(viewsets.ModelViewSet):
    queryset = Cidade.objects.all()
    serializer_class = CitiesSerializer
    permission_classes = [CustomAuthenticationPermission]
    http_method_names = ["get", "patch", "post", "delete"]

    def create(self, request, *args, **kwargs):
        data = json.loads(request.body)
        success, message, instance, http = serializer_function(data, CitiesSerializer)
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
        serializer = CitiesSerializer(queryset, many=True)
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
                + "' deletou um(a) 'Cidade' de nome '"
                + instance.name
                + "'"
            )

            create_audits(
                atumus.id,
                description,
                "Cidade",
                instance.name,
                instance.id,
            )
            instance.delete()
            response = {"success": True, "message": "Removido com sucesso"}
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {"success": False, "message": "Não encontrado"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# class ViewTransferHistoryClient(viewsets.ModelViewSet):
#     queryset = TransferHistoryClient.objects.all()
#     serializer_class = TransferHistoryClientSerializer
#     permission_classes = [CustomAuthenticationPermission]
#     http_method_names = ["get", "post"]

#     def get_queryset_list(self):
#         queryset = super().get_queryset()
#         q = Q()
#         filter_id = self.request.query_params.get("id")
#         if filter_id:
#             q &= Q(id=filter_id)
#         filter_rca = self.request.query_params.get("rca")
#         if filter_rca:
#             q &= Q(rca_added=filter_rca) | Q(rca_removed=filter_rca)
#         ordering = self.request.query_params.get("ordering")
#         if ordering:
#             queryset = queryset.order_by(ordering)

#         if self.request.query_params.get("limit") and self.request.query_params.get(
#             "offset"
#         ):
#             filter_limit = int(self.request.query_params.get("limit"))
#             filter_offset = int(self.request.query_params.get("offset"))
#             queryset = queryset.filter(q)
#             count = queryset.count()
#             queryset = queryset[filter_offset : filter_offset + filter_limit]
#         else:
#             queryset = queryset.filter(q)
#             count = queryset.count()

#         return queryset, count

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         data = serializer.data

#         response = {
#             "success": True,
#             "message": "Consulta executada com sucesso!",
#             "data": data,
#         }
#         return Response(response)

#     def list(self, request, *args, **kwargs):
#         queryset, count = self.get_queryset_list()
#         queryset = self.filter_queryset(queryset)
#         serializer = TransferHistoryClientSerializer(queryset, many=True)
#         response = {
#             "success": True,
#             "message": "Busca realizada com sucesso",
#             "total": count,
#             "data": serializer.data,
#         }
#         return Response(response, status=status.HTTP_200_OK)


# class ViewTransferClient(APIView):
#     permission_classes = [CustomAuthenticationPermission]
#     http_method_names = ["post"]

#     def transfer_client(self, request):
#         if not request.user.type == "Atumus":
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Apenas usuários Atumus podem realizar tal ação!",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         data = json.loads(request.body)
#         new_rca = Atendende.objects.filter(id=data["rca"]).first()
#         list_client_id = data["clients"]
#         for client_id in list_client_id:
#             client = Cliente.objects.filter(id=client_id).first()
#             old_rca = Atendende.objects.filter(id=client.rca.id).first()
#             client.rca = new_rca
#             client.save()
#             atumus = Gerente.objects.filter(user__id=request.user.id).first()
#             data_history = {
#                 "rca_added": new_rca.id,
#                 "rca_removed": old_rca.id,
#                 "atumus": atumus.id,
#                 "client": client.id,
#                 "message": "O cliente '"
#                 + client.name
#                 + "' foi movido do representante: '"
#                 + old_rca.name
#                 + "' para o representante : '"
#                 + new_rca.name
#                 + "' por: '"
#                 + atumus.name
#                 + "'",
#             }
#             serializer_function(data_history, TransferHistoryClientSerializer)

#         response = {
#             "success": True,
#             "message": "Modificado com sucesso!",
#             # "data": serializer.data,
#         }
#         return Response(response)

#     def rca_transfer_client(self, request):
#         if not request.user.type == "Atumus":
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Apenas usuários Atumus podem realizar tal ação!",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         data = json.loads(request.body)
#         new_rca = Atendende.objects.filter(id=data["new_rca"]).first()
#         old_rca = Atendende.objects.filter(id=data["old_rca"]).first()
#         if not new_rca or not old_rca:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Um dos representantes não existe",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         list_client = Cliente.objects.filter(rca=old_rca.id)
#         for client in list_client:
#             client.rca = new_rca
#             client.save()
#             atumus = Gerente.objects.filter(user__id=request.user.id).first()
#             data_history = {
#                 "rca_added": new_rca.id,
#                 "rca_removed": old_rca.id,
#                 "atumus": atumus.id,
#                 "client": client.id,
#                 "message": "O cliente '"
#                 + client.name
#                 + "' foi movido do representante: '"
#                 + old_rca.name
#                 + "' para o representante : '"
#                 + new_rca.name
#                 + "' por: '"
#                 + atumus.name
#                 + "'",
#             }
#             serializer_function(data_history, TransferHistoryClientSerializer)

#         response = {
#             "success": True,
#             "message": "Modificado com sucesso!",
#         }
#         return Response(response)

#     def post(self, request, action):
#         if action == "transfer-client":
#             return self.transfer_client(request)
#         elif action == "rca-transfer-client":
#             return self.rca_transfer_client(request)
#         else:
#             return Response(
#                 {"success": False, "message": "Ação inválida"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
