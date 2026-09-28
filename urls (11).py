from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

admin.site.site_header = "Copa Santa Fe — Administración"
admin.site.site_title = "Copa Santa Fe"
admin.site.index_title = "Gestión de Facturación y Cartera"

urlpatterns = [
    path("ingresar/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path("equipos/", include("equipos.urls")),
    path("", include("core.urls")),
]
