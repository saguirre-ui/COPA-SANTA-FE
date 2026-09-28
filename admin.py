from django.contrib import admin

from .models import Cuota, Factura, Pago, PlantillaGenerada


class CuotaInline(admin.TabularInline):
    model = Cuota
    extra = 0


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero_completo", "equipo", "fecha", "valor_total", "cant_cuotas", "anulada")
    list_filter = ("anulada", "fecha")
    search_fields = ("numero", "equipo__nombre_club", "equipo__documento")
    inlines = [CuotaInline]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("cuota", "fecha", "valor", "medio", "referencia")
    list_filter = ("medio",)

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(PlantillaGenerada)
