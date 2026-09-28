from django.contrib import admin

from .models import Equipo


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre_club", "razon_social", "documento", "valor", "cuotas", "seguimiento", "activo")
    list_filter = ("activo", "seguimiento")
    search_fields = ("nombre_club", "razon_social", "documento", "responsable")

    def has_delete_permission(self, request, obj=None):
        # Información contable: se desactiva, no se elimina.
        return False
