from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from equipos.models import Equipo
from facturacion.models import Factura, Pago

from .models import Configuracion, RegistroAuditoria


@login_required
def dashboard(request):
    facturas = Factura.objects.filter(anulada=False)
    total_facturado = facturas.aggregate(t=Sum("valor_total"))["t"] or Decimal("0")
    total_recaudado = Pago.objects.filter(cuota__factura__anulada=False).aggregate(t=Sum("valor"))["t"] or Decimal("0")

    contexto = {
        "config": Configuracion.obtener(),
        "total_equipos": Equipo.objects.count(),
        "equipos_activos": Equipo.objects.filter(activo=True).count(),
        "por_facturar": Equipo.objects.filter(activo=True, seguimiento=Equipo.Seguimiento.POR_FACTURAR).count(),
        "facturas_generadas": facturas.count(),
        "total_recaudado": total_recaudado,
        "cartera_total": total_facturado - total_recaudado,
        "ultimos_movimientos": RegistroAuditoria.objects.select_related("usuario")[:6],
    }
    return render(request, "core/dashboard.html", contexto)
