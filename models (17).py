"""
Tablas generales: configuracion y auditoria.

La tabla de usuarios es la de Django (auth_user): ya trae contraseñas cifradas,
grupos y permisos, que se usarán en la Fase 5.
"""
from django.conf import settings
from django.db import models


class Configuracion(models.Model):
    """
    Valores fijos que hoy están escritos dentro de las fórmulas de la hoja
    «Facturar» (plantilla World Office) y reglas generales de cartera.
    Es un registro único (id = 1), editable desde /admin.
    """

    # --- Torneo ---
    nombre_torneo = models.CharField(max_length=100, default="COPA SANTA FE")
    anio = models.PositiveSmallIntegerField("año", default=2026)
    edicion = models.CharField("edición", max_length=20, default="14.ª")
    texto_nota_factura = models.CharField(
        "texto de la nota de factura",
        max_length=200,
        default="PARTICIPACION EN COPA SANTA FE EQ INVITADOS",
        help_text="Hoja Datos, columna NOTA: se completa con el nombre del club entre paréntesis.",
    )

    # --- Encabezado World Office (hoja Facturar) ---
    empresa = models.CharField("Encab: Empresa", max_length=150, default="INDEPENDIENTE SANTA FE S.A.")
    tipo_documento = models.CharField("Encab: Tipo Documento", max_length=10, default="FV")
    prefijo = models.CharField("Encab: Prefijo", max_length=10, default="EF")
    tercero_interno = models.CharField("Encab: Tercero Interno", max_length=20, default="1026250096")
    forma_pago = models.CharField("Encab: FormaPago", max_length=30, default="Credito")
    siguiente_consecutivo = models.PositiveIntegerField(
        "siguiente Documento Número",
        default=63478,
        help_text="Último número usado en el Excel: 63477.",
    )

    # --- Detalle World Office (hoja Facturar) ---
    producto = models.CharField("Detalle: Producto", max_length=30, default="41601501")
    bodega = models.CharField("Detalle: Bodega", max_length=50, default="Principal")
    unidad_medida = models.CharField("Detalle: UnidadDeMedida", max_length=20, default="Und.")
    iva = models.DecimalField("Detalle: IVA", max_digits=5, decimal_places=2, default=0)
    centro_costos = models.CharField(
        "Detalle: Centro costos", max_length=100, default="9207 Copa Santa Fe equipos invitados"
    )

    # --- Reglas de cartera (se usan desde la Fase 2) ---
    dias_aviso_vencimiento = models.PositiveSmallIntegerField(
        "días de aviso «por vencer»",
        default=5,
        help_text="La fórmula ESTADO DE PAGO avisa cuando faltan 5 días o menos.",
    )
    dias_vencimiento_cuota_1 = models.PositiveSmallIntegerField(
        "días para vencer cuota 1",
        default=0,
        help_text="Contados desde la fecha de factura. En el Excel es 0 (vence el mismo día). PENDIENTE CONFIRMAR.",
    )
    dias_vencimiento_cuota_2 = models.PositiveSmallIntegerField(
        "días para vencer cuota 2",
        default=0,
        help_text="Contados desde la fecha de factura. En el Excel es 0 (vence el mismo día). PENDIENTE CONFIRMAR.",
    )

    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "configuración"
        verbose_name_plural = "configuración"

    def __str__(self):
        return f"{self.nombre_torneo} {self.anio} — {self.edicion} edición"

    def save(self, *args, **kwargs):
        self.pk = 1  # registro único
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # no se puede eliminar

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class RegistroAuditoria(models.Model):
    """Historial de acciones importantes. Nunca se edita ni se borra."""

    class Accion(models.TextChoices):
        CREAR_EQUIPO = "crear_equipo", "Creación de equipo"
        EDITAR_EQUIPO = "editar_equipo", "Edición de equipo"
        ACTIVAR_EQUIPO = "activar_equipo", "Activación de equipo"
        DESACTIVAR_EQUIPO = "desactivar_equipo", "Desactivación de equipo"
        CREAR_FACTURA = "crear_factura", "Creación de factura"
        EDITAR_FACTURA = "editar_factura", "Modificación de factura"
        REGISTRAR_PAGO = "registrar_pago", "Registro de pago"
        IMPORTAR = "importar", "Importación"
        EXPORTAR = "exportar", "Exportación"

    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    accion = models.CharField(max_length=30, choices=Accion.choices)
    modelo = models.CharField(max_length=50)
    objeto_id = models.CharField(max_length=50, blank=True)
    descripcion = models.CharField(max_length=255)
    cambios = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "auditoría"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.fecha:%Y-%m-%d %H:%M} — {self.get_accion_display()} — {self.descripcion}"


def registrar_auditoria(usuario, accion, objeto, descripcion, cambios=None):
    """Atajo para registrar una acción desde cualquier vista."""
    return RegistroAuditoria.objects.create(
        usuario=usuario if getattr(usuario, "is_authenticated", False) else None,
        accion=accion,
        modelo=objeto.__class__.__name__,
        objeto_id=str(objeto.pk),
        descripcion=descripcion[:255],
        cambios=cambios or {},
    )
