from django.contrib import admin

from .models import Configuracion, RegistroAuditoria


@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Torneo", {"fields": ("nombre_torneo", "anio", "edicion", "texto_nota_factura")}),
        ("Encabezado World Office", {"fields": ("empresa", "tipo_documento", "prefijo", "tercero_interno", "forma_pago", "siguiente_consecutivo")}),
        ("Detalle World Office", {"fields": ("producto", "bodega", "unidad_medida", "iva", "centro_costos")}),
        ("Reglas de cartera", {"fields": ("dias_aviso_vencimiento", "dias_vencimiento_cuota_1", "dias_vencimiento_cuota_2")}),
    )

    def has_add_permission(self, request):
        return not Configuracion.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "usuario", "accion", "descripcion")
    list_filter = ("accion", "usuario")
    search_fields = ("descripcion", "objeto_id")
    readonly_fields = [f.name for f in RegistroAuditoria._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
