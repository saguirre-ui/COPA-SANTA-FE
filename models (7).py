"""
Tabla «equipos».

Cada registro equivale a UNA FILA de la hoja «Datos» del Excel: la pareja
tercero que paga (NIT/cédula + razón social) + club. Se modela así porque en el
Excel un mismo club puede tener dos pagadores distintos (ej. REYES DEL FUTBOL).

Correspondencia con el Excel (hoja Datos):
    NOMBRE          -> razon_social
    DOCUMENTO       -> documento
    NOMBRE DEL CLUB -> nombre_club
    VALOR           -> valor
    CUOTAS          -> cuotas
    DESCUENTOS      -> descuentos
    VALOR CUOTA     -> valor_cuota   (calculado: VALOR / CUOTAS)
    SEGUIMIENTO     -> seguimiento
    NOVEDADES       -> se calculará desde las facturas (Fase 2)
    NOTA            -> nota_factura  (calculada)

Campos nuevos (no existen en el Excel, pedidos para la gestión de cobro):
    digito_verificacion, responsable, correo, telefono, direccion, activo.
"""
import re
from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse


def normalizar_texto(valor: str) -> str:
    """Quita espacios sobrantes y pasa a mayúsculas (evita 'MANAOS FC ' vs 'MANAOS FC')."""
    return re.sub(r"\s+", " ", (valor or "")).strip().upper()


solo_digitos = RegexValidator(r"^\d+$", "Escriba solo números, sin puntos, guiones ni dígito de verificación.")


class Equipo(models.Model):
    class Seguimiento(models.TextChoices):
        POR_FACTURAR = "Por facturar", "Por facturar"
        FACTURADO = "Facturado", "Facturado"

    # --- Datos del equipo ---
    nombre_club = models.CharField("nombre del club", max_length=150)

    # --- Información tributaria / facturación ---
    razon_social = models.CharField(
        "razón social / persona natural",
        max_length=200,
        help_text="A nombre de quien se factura (columna NOMBRE de la hoja Datos).",
    )
    documento = models.CharField(
        "NIT / cédula",
        max_length=20,
        validators=[solo_digitos],
        help_text="Sin dígito de verificación. Es el «Tercero Externo» en World Office.",
    )
    digito_verificacion = models.CharField(
        "DV", max_length=1, blank=True, validators=[RegexValidator(r"^\d$", "Un solo dígito.")]
    )

    # --- Condiciones comerciales (hoja Datos) ---
    valor = models.DecimalField(
        "valor", max_digits=14, decimal_places=0, validators=[MinValueValidator(Decimal("0"))]
    )
    cuotas = models.PositiveSmallIntegerField("cuotas", default=2, validators=[MinValueValidator(1)])
    descuentos = models.DecimalField(
        "descuentos", max_digits=14, decimal_places=0, default=0, validators=[MinValueValidator(Decimal("0"))]
    )
    seguimiento = models.CharField(max_length=20, choices=Seguimiento.choices, default=Seguimiento.POR_FACTURAR)

    # --- Contacto (campos nuevos, opcionales) ---
    responsable = models.CharField(max_length=150, blank=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField("teléfono", max_length=30, blank=True)
    direccion = models.CharField("dirección", max_length=200, blank=True)

    # --- Control ---
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "equipo"
        verbose_name_plural = "equipos"
        ordering = ["nombre_club", "razon_social"]
        constraints = [
            models.UniqueConstraint(fields=["documento", "nombre_club"], name="equipo_unico_documento_club"),
        ]
        indexes = [models.Index(fields=["documento"]), models.Index(fields=["activo"])]

    def __str__(self):
        return self.nombre_club

    def save(self, *args, **kwargs):
        self.nombre_club = normalizar_texto(self.nombre_club)
        self.razon_social = normalizar_texto(self.razon_social)
        self.documento = re.sub(r"\D", "", self.documento or "")
        self.correo = (self.correo or "").strip().lower()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("equipos:detalle", args=[self.pk])

    # --- Valores calculados (igual que en el Excel) ---
    @property
    def codigo(self):
        """Identificador interno visible: EQ-0001."""
        return f"EQ-{self.pk:04d}" if self.pk else "—"

    @property
    def valor_cuota(self):
        """Hoja Datos, VALOR CUOTA = VALOR / CUOTAS."""
        return (self.valor / self.cuotas) if self.cuotas else self.valor

    @property
    def nota_factura(self):
        """Hoja Datos, NOTA = "PARTICIPACION EN COPA SANTA FE EQ INVITADOS (" & club & ")"."""
        from core.models import Configuracion

        return f"{Configuracion.obtener().texto_nota_factura} ({self.nombre_club})"

    @property
    def documento_con_dv(self):
        return f"{self.documento}-{self.digito_verificacion}" if self.digito_verificacion else self.documento

    @property
    def alertas_facturacion(self):
        """Problemas que impedirían facturar bien (detectados en el análisis del Excel)."""
        avisos = []
        if len(self.documento) == 10 and self.documento.startswith(("8", "9")) and not self.digito_verificacion:
            avisos.append(
                "El NIT tiene 10 dígitos: puede incluir el dígito de verificación pegado. "
                "Verifique cómo está creado el tercero en World Office."
            )
        if not self.razon_social:
            avisos.append("Falta la razón social: la factura no podría emitirse.")
        return avisos

    @property
    def alertas(self):
        """Todas las advertencias, incluidas las de contacto para cobro."""
        avisos = list(self.alertas_facturacion)
        if not (self.correo or self.telefono):
            avisos.append("No hay correo ni teléfono para gestionar el cobro.")
        return avisos
