from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import RegistroAuditoria, registrar_auditoria
from facturacion.models import Factura, Pago

from .forms import EquipoForm
from .models import Equipo

CERO = Value(Decimal("0"), output_field=DecimalField(max_digits=14, decimal_places=0))


def equipos_con_saldo():
    """Anota facturas, total facturado, total pagado y saldo sin duplicar sumas."""
    facturado = (
        Factura.objects.filter(equipo=OuterRef("pk"), anulada=False)
        .values("equipo")
        .annotate(t=Sum("valor_total"))
        .values("t")
    )
    pagado = (
        Pago.objects.filter(cuota__factura__equipo=OuterRef("pk"), cuota__factura__anulada=False)
        .values("cuota__factura__equipo")
        .annotate(t=Sum("valor"))
        .values("t")
    )
    return Equipo.objects.annotate(
        num_facturas=Count("facturas", filter=Q(facturas__anulada=False), distinct=True),
        total_facturado=Coalesce(Subquery(facturado), CERO),
        total_pagado=Coalesce(Subquery(pagado), CERO),
    )


@login_required
def lista(request):
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activos")
    seguimiento = request.GET.get("seguimiento", "")

    equipos = equipos_con_saldo()
    if q:
        equipos = equipos.filter(
            Q(nombre_club__icontains=q)
            | Q(razon_social__icontains=q)
            | Q(documento__icontains=q)
            | Q(responsable__icontains=q)
            | Q(correo__icontains=q)
        )
    if estado == "activos":
        equipos = equipos.filter(activo=True)
    elif estado == "inactivos":
        equipos = equipos.filter(activo=False)
    if seguimiento in Equipo.Seguimiento.values:
        equipos = equipos.filter(seguimiento=seguimiento)

    pagina = Paginator(equipos, 25).get_page(request.GET.get("pagina"))
    for e in pagina:
        e.saldo = e.total_facturado - e.total_pagado

    return render(
        request,
        "equipos/lista.html",
        {
            "pagina": pagina,
            "total": equipos.count(),
            "q": q,
            "estado": estado,
            "seguimiento": seguimiento,
            "opciones_seguimiento": Equipo.Seguimiento.choices,
        },
    )


@login_required
def detalle(request, pk):
    equipo = get_object_or_404(equipos_con_saldo(), pk=pk)
    equipo.saldo = equipo.total_facturado - equipo.total_pagado
    facturas = equipo.facturas.filter(anulada=False).prefetch_related("cuotas")
    pagos = Pago.objects.filter(cuota__factura__equipo=equipo).select_related("cuota__factura")
    historial = RegistroAuditoria.objects.filter(modelo="Equipo", objeto_id=str(equipo.pk))[:10]
    return render(
        request,
        "equipos/detalle.html",
        {"equipo": equipo, "facturas": facturas, "pagos": pagos, "historial": historial},
    )


@login_required
def crear(request):
    form = EquipoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        equipo = form.save()
        registrar_auditoria(
            request.user, RegistroAuditoria.Accion.CREAR_EQUIPO, equipo,
            f"Se creó el equipo {equipo.nombre_club} ({equipo.documento})",
        )
        messages.success(request, f"Equipo {equipo.nombre_club} creado.")
        return redirect(equipo)
    return render(request, "equipos/formulario.html", {"form": form, "titulo": "Nuevo equipo"})


@login_required
def editar(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    form = EquipoForm(request.POST or None, instance=equipo)
    if request.method == "POST" and form.is_valid():
        cambios = {
            campo: {"antes": str(form.initial.get(campo, "")), "despues": str(form.cleaned_data.get(campo, ""))}
            for campo in form.changed_data
        }
        equipo = form.save()
        if cambios:
            registrar_auditoria(
                request.user, RegistroAuditoria.Accion.EDITAR_EQUIPO, equipo,
                f"Se editó el equipo {equipo.nombre_club}: {', '.join(cambios)}", cambios,
            )
        messages.success(request, "Cambios guardados.")
        return redirect(equipo)
    return render(request, "equipos/formulario.html", {"form": form, "titulo": f"Editar {equipo.nombre_club}", "equipo": equipo})


@login_required
@require_POST
def cambiar_estado(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    equipo.activo = not equipo.activo
    equipo.save(update_fields=["activo", "actualizado"])
    accion = RegistroAuditoria.Accion.ACTIVAR_EQUIPO if equipo.activo else RegistroAuditoria.Accion.DESACTIVAR_EQUIPO
    texto = "activado" if equipo.activo else "desactivado"
    registrar_auditoria(request.user, accion, equipo, f"Equipo {equipo.nombre_club} {texto}")
    messages.success(request, f"Equipo {texto}.")
    return redirect(equipo)
