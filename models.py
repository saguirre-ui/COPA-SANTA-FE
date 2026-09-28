"""
Tablas «facturas», «cuotas», «pagos» y «plantillas».

Se crean desde la Fase 1 para dejar lista la estructura y las relaciones.
Las pantallas para usarlas se construyen en las Fases 2 a 4.

Correspondencia con el Excel:
    Registro Facturas (Tabla1) + Pagadas (Tabla13)  -> Factura (una sola tabla;
        "pagada" deja de ser una hoja aparte y pasa a ser un estado calculado)
    LINK / VENC. / VALOR CUOTA 1 y 2 + hoja WOMPI    -> Cuota
    Casillas $ y $2                                  -> Pago (con fecha, valor y referencia)
    Hoja Facturar (plantilla World Office)           -> PlantillaGenerada
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from equipos.models import Equipo


class Factura(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.PROTECT, related_name="facturas")
    prefijo = models.CharField(max_length=10, default="FV EF", help_text="En el Excel: 'FV EF'.")
    numero = models.PositiveIntegerField("número", help_text="Solo el número, ej. 53003.")
    fecha = models.DateField()
    valor_total = models.DecimalField(
        "valor total", max_digits=14, decimal_places=0, validators=[MinValueValidator(Decimal("1"))]
    )
    cant_cuotas = models.PositiveSmallIntegerField("cant. cuotas", default=2)
    nota = models.CharField(max_length=255, blank=True)
    marcada_para_plantilla = models.BooleanField(
        "facturar", default=False, help_text="Equivale a escribir «Facturar» en la columna FACTURAR."
    )
    anulada = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "factura"
        verbose_name_plural = "facturas"
        ordering = ["-fecha", "-numero"]
        constraints = [models.UniqueConstraint(fields=["prefijo", "numero"], name="factura_numero_unico")]

    def __str__(self):
        return self.numero_completo

    @property
    def numero_completo(self):
        """Formato del Excel: 'FV EF 53003'."""
        return f"{self.prefijo} {self.numero}"

    @property
    def total_pagado(self):
        return Pago.objects.filter(cuota__factura=self).aggregate(t=Sum("valor"))["t"] or Decimal("0")

    @property
    def saldo(self):
        """Saldo = Valor factura - Pagos registrados."""
        return self.valor_total - self.total_pagado


class Cuota(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.PROTECT, related_name="cuotas")
    numero = models.PositiveSmallIntegerField("cuota n.º")
    valor = models.DecimalField(max_digits=14, decimal_places=0, validators=[MinValueValidator(Decimal("1"))])
    vencimiento = models.DateField()
    link_pago = models.URLField("link Wompi", blank=True)

    class Meta:
        verbose_name = "cuota"
        verbose_name_plural = "cuotas"
        ordering = ["factura", "numero"]
        constraints = [models.UniqueConstraint(fields=["factura", "numero"], name="cuota_unica_por_factura")]

    def __str__(self):
        return f"{self.factura} — cuota {self.numero}"

    @property
    def descripcion_wompi(self):
        """Hoja WOMPI: 'PARTICIPACION COPA SANTA FE ' & club & ' CUOTA n'."""
        return f"PARTICIPACION COPA SANTA FE {self.factura.equipo.nombre_club} CUOTA {self.numero}"


class Pago(models.Model):
    """Historial de pagos. Desde la interfaz nunca se elimina."""

    class Medio(models.TextChoices):
        WOMPI = "Wompi", "Wompi"
        TRANSFERENCIA = "Transferencia", "Transferencia"
        CONSIGNACION = "Consignación", "Consignación"
        EFECTIVO = "Efectivo", "Efectivo"
        OTRO = "Otro", "Otro"

    cuota = models.ForeignKey(Cuota, on_delete=models.PROTECT, related_name="pagos")
    fecha = models.DateField("fecha de pago")
    valor = models.DecimalField(max_digits=14, decimal_places=0, validators=[MinValueValidator(Decimal("1"))])
    medio = models.CharField("medio de pago", max_length=20, choices=Medio.choices, default=Medio.WOMPI)
    referencia = models.CharField("referencia del pago", max_length=100, blank=True)
    observacion = models.CharField("observación", max_length=255, blank=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ["-fecha", "-creado"]

    def __str__(self):
        return f"{self.cuota} — ${self.valor:,.0f}"


class PlantillaGenerada(models.Model):
    """Cada archivo de importación World Office generado (Fase 4)."""

    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    facturas = models.ManyToManyField(Factura, related_name="plantillas")
    consecutivo_inicial = models.PositiveIntegerField(null=True, blank=True)
    consecutivo_final = models.PositiveIntegerField(null=True, blank=True)
    nombre_archivo = models.CharField(max_length=200, blank=True)
    observacion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "plantilla generada"
        verbose_name_plural = "plantillas generadas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Plantilla {self.fecha:%Y-%m-%d %H:%M}"
