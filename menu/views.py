# import datetime, json, random, pytz
# from django.contrib.auth.hashers import check_password, make_password
# from django.db.models.functions import TruncDate
# from django.http import JsonResponse
# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.response import Response
# from django.contrib.auth import logout
# from django.db.models import Q, Count
# from rest_framework.pagination import LimitOffsetPagination
# from django.utils import timezone
# from s3image import get_url, aws_image
# from drop.models import Pedido, IdentificationTillages
# from questionnaires.models import Questionnaires
# from datetime import timedelta


# class ViewMenu(APIView):
#     permission_classes = []
#     http_method_names = ["get"]

#     def get(self, request):
#         menu_atmus = {
#             "success": True,
#             "pages": [
#                 {
#                     "id": 1,
#                     "section": "Dashboard",
#                     "routes": [
#                         {
#                             "id": 101,
#                             "title": "Dashboard",
#                             "root": True,
#                             "icon": "chart-pie",
#                             "page": "/",
#                             "submenu": [],
#                         }
#                     ],
#                 },
#                 {
#                     "id": 2,
#                     "section": "Administração",
#                     "routes": [
#                         {
#                             "id": 201,
#                             "title": "Atumus",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/atumus/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 202,
#                             "title": "Coordenadores",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/coordenadores/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 203,
#                             "title": "Supervisores",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/supervisores/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 204,
#                             "title": "RCAs",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/rca/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 205,
#                             "title": "Clientes",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/clientes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 206,
#                             "title": "Cidades",
#                             "root": True,
#                             "icon": "city",
#                             "page": "/cidades/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 3,
#                     "section": "Produtos",
#                     "routes": [
#                         {
#                             "id": 301,
#                             "title": "Produtos",
#                             "root": True,
#                             "icon": "bottle-water",
#                             "page": "/produtos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 302,
#                             "title": "Tipos de produto",
#                             "root": True,
#                             "icon": "bottle-droplet",
#                             "page": "/produtos/tipos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 303,
#                             "title": "Fabricantes de produto",
#                             "root": True,
#                             "icon": "industry",
#                             "page": "/produtos/fabricantes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 304,
#                             "title": "Fornecedores de produto",
#                             "root": True,
#                             "icon": "truck-field",
#                             "page": "/produtos/fornecedores/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 4,
#                     "section": "Visitas",
#                     "routes": [
#                         {
#                             "id": 401,
#                             "title": "Bio Scan",
#                             "root": True,
#                             "icon": "leaf",
#                             "page": "/bio-scan/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 402,
#                             "title": "Fechamento de rua",
#                             "root": True,
#                             "icon": "wheat-awn",
#                             "page": "/fechamento-de-rua/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 403,
#                             "title": "Questionários",
#                             "root": True,
#                             "icon": "clipboard-question",
#                             "page": "/questionarios/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 5,
#                     "section": "Auditoria",
#                     "routes": [
#                         {
#                             "id": 501,
#                             "title": "Auditoria",
#                             "root": True,
#                             "icon": "book",
#                             "page": "/auditoria",
#                             "submenu": [],
#                         }
#                     ],
#                 },
#             ],
#         }
#         menu_coordinates = {
#             "success": True,
#             "pages": [
#                 {
#                     "id": 1,
#                     "section": "Dashboard",
#                     "routes": [
#                         {
#                             "id": 101,
#                             "title": "Dashboard",
#                             "root": True,
#                             "icon": "chart-pie",
#                             "page": "/",
#                             "submenu": [],
#                         }
#                     ],
#                 },
#                 {
#                     "id": 2,
#                     "section": "Administração",
#                     "routes": [
#                         {
#                             "id": 203,
#                             "title": "Supervisores",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/supervisores/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 204,
#                             "title": "RCAs",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/rca/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 205,
#                             "title": "Clientes",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/clientes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 206,
#                             "title": "Cidades",
#                             "root": True,
#                             "icon": "city",
#                             "page": "/cidades/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 3,
#                     "section": "Produtos",
#                     "routes": [
#                         {
#                             "id": 301,
#                             "title": "Produtos",
#                             "root": True,
#                             "icon": "bottle-water",
#                             "page": "/produtos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 302,
#                             "title": "Tipos de produto",
#                             "root": True,
#                             "icon": "bottle-droplet",
#                             "page": "/produtos/tipos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 303,
#                             "title": "Fabricantes de produto",
#                             "root": True,
#                             "icon": "industry",
#                             "page": "/produtos/fabricantes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 304,
#                             "title": "Fornecedores de produto",
#                             "root": True,
#                             "icon": "truck-field",
#                             "page": "/produtos/fornecedores/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 4,
#                     "section": "Visitas",
#                     "routes": [
#                         {
#                             "id": 401,
#                             "title": "Bio Scan",
#                             "root": True,
#                             "icon": "leaf",
#                             "page": "/bio-scan/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 402,
#                             "title": "Fechamento de rua",
#                             "root": True,
#                             "icon": "wheat-awn",
#                             "page": "/fechamento-de-rua/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 403,
#                             "title": "Questionários",
#                             "root": True,
#                             "icon": "clipboard-question",
#                             "page": "/questionarios/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#             ],
#         }
#         menu_supervisors = {
#             "success": True,
#             "pages": [
#                 {
#                     "id": 1,
#                     "section": "Dashboard",
#                     "routes": [
#                         {
#                             "id": 101,
#                             "title": "Dashboard",
#                             "root": True,
#                             "icon": "chart-pie",
#                             "page": "/",
#                             "submenu": [],
#                         }
#                     ],
#                 },
#                 {
#                     "id": 2,
#                     "section": "Administração",
#                     "routes": [
#                         {
#                             "id": 204,
#                             "title": "RCAs",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/rca/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 205,
#                             "title": "Clientes",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/clientes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 206,
#                             "title": "Cidades",
#                             "root": True,
#                             "icon": "city",
#                             "page": "/cidades/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 3,
#                     "section": "Produtos",
#                     "routes": [
#                         {
#                             "id": 301,
#                             "title": "Produtos",
#                             "root": True,
#                             "icon": "bottle-water",
#                             "page": "/produtos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 302,
#                             "title": "Tipos de produto",
#                             "root": True,
#                             "icon": "bottle-droplet",
#                             "page": "/produtos/tipos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 303,
#                             "title": "Fabricantes de produto",
#                             "root": True,
#                             "icon": "industry",
#                             "page": "/produtos/fabricantes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 304,
#                             "title": "Fornecedores de produto",
#                             "root": True,
#                             "icon": "truck-field",
#                             "page": "/produtos/fornecedores/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 4,
#                     "section": "Visitas",
#                     "routes": [
#                         {
#                             "id": 401,
#                             "title": "Bio Scan",
#                             "root": True,
#                             "icon": "leaf",
#                             "page": "/bio-scan/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 402,
#                             "title": "Fechamento de rua",
#                             "root": True,
#                             "icon": "wheat-awn",
#                             "page": "/fechamento-de-rua/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 403,
#                             "title": "Questionários",
#                             "root": True,
#                             "icon": "clipboard-question",
#                             "page": "/questionarios/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#             ],
#         }
#         menu_rcas = {
#             "success": True,
#             "pages": [
#                 {
#                     "id": 1,
#                     "section": "Dashboard",
#                     "routes": [
#                         {
#                             "id": 101,
#                             "title": "Dashboard",
#                             "root": True,
#                             "icon": "chart-pie",
#                             "page": "/",
#                             "submenu": [],
#                         }
#                     ],
#                 },
#                 {
#                     "id": 2,
#                     "section": "Administração",
#                     "routes": [
#                         {
#                             "id": 205,
#                             "title": "Clientes",
#                             "root": True,
#                             "icon": "user-group",
#                             "page": "/clientes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 206,
#                             "title": "Cidades",
#                             "root": True,
#                             "icon": "city",
#                             "page": "/cidades/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 3,
#                     "section": "Produtos",
#                     "routes": [
#                         {
#                             "id": 301,
#                             "title": "Produtos",
#                             "root": True,
#                             "icon": "bottle-water",
#                             "page": "/produtos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 302,
#                             "title": "Tipos de produto",
#                             "root": True,
#                             "icon": "bottle-droplet",
#                             "page": "/produtos/tipos/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 303,
#                             "title": "Fabricantes de produto",
#                             "root": True,
#                             "icon": "industry",
#                             "page": "/produtos/fabricantes/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 304,
#                             "title": "Fornecedores de produto",
#                             "root": True,
#                             "icon": "truck-field",
#                             "page": "/produtos/fornecedores/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#                 {
#                     "id": 4,
#                     "section": "Visitas",
#                     "routes": [
#                         {
#                             "id": 401,
#                             "title": "Bio Scan",
#                             "root": True,
#                             "icon": "leaf",
#                             "page": "/bio-scan/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 402,
#                             "title": "Fechamento de rua",
#                             "root": True,
#                             "icon": "wheat-awn",
#                             "page": "/fechamento-de-rua/",
#                             "submenu": [],
#                         },
#                         {
#                             "id": 403,
#                             "title": "Questionários",
#                             "root": True,
#                             "icon": "clipboard-question",
#                             "page": "/questionarios/",
#                             "submenu": [],
#                         },
#                     ],
#                 },
#             ],
#         }
#         if request.user.type == "Atumus":
#             menu = menu_atmus
#         if request.user.type == "Coordinators":
#             menu = menu_coordinates
#         if request.user.type == "Supervisors":
#             menu = menu_supervisors
#         if request.user.type == "RCAs":
#             menu = menu_rcas
#         return Response(
#             {"success": True, "message": "Busca realizada com sucesso", "data": menu},
#             status=status.HTTP_200_OK,
#         )
