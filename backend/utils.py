from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    MethodNotAllowed,
)
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

# from users.models import Privileges


def custom_exception_handler(exc, context):
    response = {}
    print("AAAAAA ", type(exc))
    if isinstance(exc, AuthenticationFailed):
        response["success"] = False
        response["message"] = "Usuário não autenticado."
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, NotAuthenticated):
        response["success"] = False
        response["message"] = "Usuário não autenticado."
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, Http404):
        response["success"] = False
        response["message"] = "Objeto não encontrado."
        status_code = status.HTTP_404_NOT_FOUND
    # elif isinstance(exc, Privileges.DoesNotExist):
    #     response["success"] = False
    #     response["message"] = "Privilegio não encontrado."
    #     status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, UnboundLocalError):
        response["success"] = False
        response["message"] = "Objeto não encontrado"
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, MethodNotAllowed):
        response["success"] = False
        response["message"] = "Método não permitido para esta rota."
        status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    else:
        response["detail"] = str(exc)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(response, status=status_code)
