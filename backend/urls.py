from django.urls import include, path
from rest_framework.routers import DefaultRouter
from audits.views import ViewAuditsRemoval
from drop.views import (
    ViewProducts,
    ViewStatusIdentifications,
    ViewTypeProducts,
)
from function.views import ViewSuccess

# from menu.views import ViewMenu
from users.views import (
    ViewAtumus,
    ViewCities,
    ViewClients,
    ViewCoordinators,
    ViewEmailVerify,
    ViewLogin,
    ViewProfile,
    ViewRCAs,
    ViewSupervisors,
    ViewUsers,
)

root = DefaultRouter()
root.register(r"status/identification", ViewStatusIdentifications)
root.register(r"users", ViewUsers)
root.register(r"atumus", ViewAtumus)
root.register(r"coordinators", ViewCoordinators)
root.register(r"supervisors", ViewSupervisors)
root.register(r"rcas", ViewRCAs)
root.register(r"clients", ViewClients)
root.register(r"cities", ViewCities)
root.register(r"products", ViewProducts)
root.register(r"type/products", ViewTypeProducts)
root.register(r"audits", ViewAuditsRemoval)

urlpatterns = [
    path("", ViewSuccess.ok),
    path("", include(root.urls)),
    path("login/", ViewLogin.as_view(), {"action": "login"}, name="login"),
    path(
        "forgot-password/",
        ViewLogin.as_view(),
        {"action": "forgotten"},
        name="forgotten",
    ),
    path("reset-password/", ViewLogin.as_view(), {"action": "reset"}, name="reset"),
    path("refresh-token/", ViewLogin.as_view(), {"action": "refresh"}, name="refresh"),
    path("check-hash/", ViewLogin.as_view(), {"action": "check"}, name="check"),
    path("profile/", ViewProfile.as_view(), name="profile"),
    path("email-verify/", ViewEmailVerify.as_view(), name="email-verify"),
    # path("menu/", ViewMenu.as_view(), name="menu"),
    # path(
    #     "transfer-client/",
    #     ViewTransferClient.as_view(),
    #     {"action": "transfer-client"},
    #     name="transfer-client",
    # ),
    # path(
    #     "rca-transfer-client/",
    #     ViewTransferClient.as_view(),
    #     {"action": "rca-transfer-client"},
    #     name="rca-transfer-client",
    # ),
    # path(
    #     "dashboard/client-count-paper/",
    #     ViewDashboard.as_view(),
    #     {"action": "client-count-paper"},
    #     name="client-count-paper",
    # ),
    # path(
    #     "dashboard/clients-fill-tillage/",
    #     ViewDashboard.as_view(),
    #     {"action": "clients-fill-tillage"},
    #     name="clients-fill-tillage",
    # ),
    # path(
    #     "dashboard/most-visited-cities/",
    #     ViewDashboard.as_view(),
    #     {"action": "most-visited-cities"},
    #     name="most-visited-cities",
    # ),
    # path(
    #     "dashboard/rca-count/",
    #     ViewDashboard.as_view(),
    #     {"action": "rca-count"},
    #     name="rca-count",
    # ),
]
