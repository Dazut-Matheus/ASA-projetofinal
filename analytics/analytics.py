# import datetime, json, random, pytz
# from django.contrib.auth.hashers import check_password, make_password
# from django.db.models.functions import TruncDate
# from django.http import JsonResponse
# from rest_framework import viewsets, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.contrib.auth import logout
# from django.db.models import Q, Count, Sum
# from django.utils import timezone
# from s3image import get_url, aws_image
# from drop.models import Pedido
# from questionnaires.models import Questionnaires
# from datetime import timedelta, datetime
# from dateutil.relativedelta import relativedelta
# from operator import itemgetter
# from users.models import Cidade
# from users.serializer import CitiesSerializer


# class ViewDashboard(APIView):
#     permission_classes = []
#     http_method_names = ["post", "get"]

#     def post(self, request, action):
#         if action == "client-count-paper":
#             return self.client_count_paper(request)
#         elif action == "clients-fill-tillage":
#             return self.clients_fill_tillage(request)
#         elif action == "rca-count":
#             return self.rca_count(request)
#         else:
#             return Response(
#                 {"success": False, "message": "Ação inválida"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     def client_count_paper(self, request):
#         data = json.loads(request.body)
#         q = Q()
#         if "rca" in data.keys():
#             q &= Q(client__rca__id=data["rca"])

#         list_data = []

#         if data["filter_type"] == "weekly":
#             current_date = timezone.now() + timedelta(days=1)
#             one_week_ago = current_date - timedelta(weeks=1) + timedelta(days=1)
#             current_date = current_date.date()
#             one_week_ago = one_week_ago.date()
#             queryset = Pedido.objects.filter(
#                 created_at__range=[one_week_ago, current_date]
#             ).values("created_at", "client__id")
#             result = (
#                 queryset.annotate(day=TruncDate("created_at"))
#                 .values("day")
#                 .annotate(count=Count("client__id", distinct=True))
#             )
#             count_dict = {item["day"]: item["count"] for item in result}
#             date_list = [
#                 one_week_ago + timedelta(days=i)
#                 for i in range((current_date - one_week_ago).days + 1)
#             ]
#             for day in date_list:
#                 count = count_dict.get(day, 0)
#                 list_data.append({"label": day, "count": count})

#         if data["filter_type"] == "biweekly":
#             current_date = timezone.now() + timedelta(days=1)
#             two_week_ago = current_date - timedelta(weeks=2)
#             current_date = current_date.date()
#             two_week_ago = two_week_ago.date()
#             queryset = Pedido.objects.filter(
#                 created_at__range=[two_week_ago, current_date]
#             ).values("created_at", "client__id")
#             result = (
#                 queryset.annotate(day=TruncDate("created_at"))
#                 .values("day")
#                 .annotate(count=Count("client__id", distinct=True))
#             )
#             count_dict = {item["day"]: item["count"] for item in result}
#             date_list = [
#                 two_week_ago + timedelta(days=i)
#                 for i in range((current_date - two_week_ago).days + 1)
#             ]
#             for day in date_list:
#                 count = count_dict.get(day, 0)
#                 list_data.append({"label": day, "count": count})

#         if data["filter_type"] == "monthly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = current_date - relativedelta(years=1)
#             initial_date = initial_date.date()
#             current_date = current_date.date()

#             current_year = current_date.year
#             current_month = current_date.month

#             year = initial_date.year
#             month = initial_date.month

#             queryset = Pedido.objects.filter(
#                 created_at__range=[initial_date, current_date]
#             )

#             while (year, month) <= (current_year, current_month):
#                 month_start = datetime(year, month, 1)
#                 month_end = month_start + relativedelta(months=1) - timedelta(days=1)
#                 count = (
#                     queryset.filter(created_at__range=[month_start, month_end])
#                     .values("client__id")
#                     .distinct()
#                     .count()
#                 )

#                 list_data.append(
#                     {"label": str(month) + "/" + str(year), "count": count}
#                 )
#                 if month == 12:
#                     year += 1
#                     month = 1
#                 else:
#                     month += 1

#         return Response(
#             {"success": True, "message": "Sucesso", "data": list_data},
#             status=status.HTTP_200_OK,
#         )

#     def clients_fill_tillage(self, request):
#         data = json.loads(request.body)
#         q = Q()

#         # Filtro de data
#         if "rca" in data.keys():
#             q &= Q(client__rca__id=data["rca"])

#         if data["filter_type"] == "daily":
#             current_date = timezone.now()
#             q &= Q(created_at__date=current_date)

#         if data["filter_type"] == "weekly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = current_date - timedelta(weeks=1) + timedelta(days=1)
#             current_date = current_date.date()
#             initial_date = initial_date.date()
#             q &= Q(created_at__range=[initial_date, current_date])

#         if data["filter_type"] == "monthly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = timezone.now() - relativedelta(months=1)
#             current_date = current_date.date()
#             initial_date = initial_date.date()
#             q &= Q(created_at__range=[initial_date, current_date])

#         if data["filter_type"] == "yearly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = timezone.now() - relativedelta(years=1)
#             current_date = current_date.date()
#             initial_date = initial_date.date()
#             q &= Q(created_at__range=[initial_date, current_date])

#         q1 = Q()
#         q2 = Q()
#         q1 &= Q(fill_percentage_after_with_product__gte=80)
#         q2 &= Q(fill_percentage_after_with_product__lt=80)

#         client_count_above_80 = IdentificationTillages.objects.filter(q).count()
#         client_count_under_80 = IdentificationTillages.objects.filter(q).count()

#         return Response(
#             {
#                 "success": True,
#                 "message": "Sucesso",
#                 "data": {
#                     "above_80": client_count_above_80,
#                     "under_80": client_count_under_80,
#                 },
#             },
#             status=status.HTTP_200_OK,
#         )

#     def most_visited_cities(self, request):
#         q = Q()
#         list_city_paper = (
#             Pedido.objects.filter(q)
#             .values("client__city__id")
#             .annotate(count=Count("id"))
#         )
#         list_city_tillage = (
#             IdentificationTillages.objects.filter(q)
#             .values("client__city__id")
#             .annotate(count=Count("id"))
#         )

#         combined_list = list(list_city_paper) + list(list_city_tillage)
#         print(combined_list)
#         city_counts = {}
#         if combined_list == []:
#             return Response(
#                 {"success": True, "message": "Sucesso", "data": []},
#                 status=status.HTTP_200_OK,
#             )
#         for item in combined_list:
#             city = item["client__city__id"]
#             count = item["count"]
#             if city in city_counts:
#                 city_counts[city] += count
#             else:
#                 city_counts[city] = count
#         city = Cidade.objects.filter(id=city).first()
#         data_city = CitiesSerializer(city).data
#         result = [
#             {"city": data_city, "count": count} for city, count in city_counts.items()
#         ]
#         sorted_result = sorted(result, key=itemgetter("count"), reverse=True)

#         return Response(
#             {"success": True, "message": "Sucesso", "data": sorted_result},
#             status=status.HTTP_200_OK,
#         )

#     def rca_count(self, request):
#         data = json.loads(request.body)
#         q = Q()

#         if data["filter_type"] == "daily":
#             current_date = timezone.now()
#             q &= Q(created_at__date=current_date)

#         if data["filter_type"] == "weekly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = current_date - timedelta(weeks=1) + timedelta(days=1)
#             current_date = current_date.date()
#             initial_date = initial_date.date()
#             q &= Q(created_at__range=[initial_date, current_date])

#         if data["filter_type"] == "monthly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = timezone.now() - relativedelta(months=1)
#             current_date = current_date.date()
#             initial_date = initial_date.date()
#             q &= Q(created_at__range=[initial_date, current_date])

#         if data["filter_type"] == "yearly":
#             current_date = timezone.now() + timedelta(days=1)
#             initial_date = timezone.now() - relativedelta(years=1)
#             current_date = current_date.date()
#             initial_date = initial_date.date()
#             q &= Q(created_at__range=[initial_date, current_date])

#         q1 = Q()
#         q2 = Q()
#         q1 &= Q(fill_percentage_after_with_product__gte=80)
#         q2 &= Q(fill_percentage_after_with_product__lt=80)

#         identification_tillage = (
#             IdentificationTillages.objects.filter(q)
#             .values("client__rca__id")
#             .distinct()
#             .annotate(count=Count("client__rca__id", distinct=True))
#         )
#         count_tillage = 0
#         for item in identification_tillage:
#             count_tillage += item["count"]
#         identification_paper = (
#             Pedido.objects.filter(q)
#             .values("client__rca__id")
#             .distinct()
#             .annotate(count=Count("client__rca__id", distinct=True))
#         )
#         count_paper = 0
#         for item in identification_paper:
#             count_paper += item["count"]

#         return Response(
#             {
#                 "success": True,
#                 "message": "Sucesso",
#                 "data": {
#                     "identification_tillage": count_tillage,
#                     "identification_paper": count_paper,
#                 },
#             },
#             status=status.HTTP_200_OK,
#         )

#     def get(self, request, action):
#         if action == "most-visited-cities":
#             return self.most_visited_cities(request)
#         else:
#             return Response(
#                 {"success": False, "message": "Ação inválida"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
