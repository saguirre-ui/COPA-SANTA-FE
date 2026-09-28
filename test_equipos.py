from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Configuracion, RegistroAuditoria
from equipos.models import Equipo
from facturacion.models import Cuota, Factura, Pago


def crear_equipo(**extra):
    datos = dict(nombre_club="GIBOR FC", razon_social="JOSE DAVID RIVEROS SANTA", documento="1000860202",
                 valor=Decimal("1500000"), cuotas=2)
    datos.update(extra)
    return Equipo.objects.create(**datos)


class ModeloEquipoTests(TestCase):
    def test_normaliza_espacios_y_mayusculas(self):
        e = crear_equipo(nombre_club="  manaos   fc ", documento="80.175.893")
        self.assertEqual(e.nombre_club, "MANAOS FC")
        self.assertEqual(e.documento, "80175893")

    def test_valor_cuota_y_nota_como_en_excel(self):
        e = crear_equipo()
        self.assertEqual(e.valor_cuota, Decimal("750000"))
        self.assertEqual(e.nota_factura, "PARTICIPACION EN COPA SANTA FE EQ INVITADOS (GIBOR FC)")

    def test_alerta_nit_con_dv_pegado(self):
        e = crear_equipo(nombre_club="KANTERANOS", documento="9008138554")
        self.assertTrue(any("10 dígitos" in a for a in e.alertas))

    def test_mismo_club_con_dos_pagadores_es_valido(self):
        crear_equipo(nombre_club="REYES DEL FUTBOL", documento="800222095")
        crear_equipo(nombre_club="REYES DEL FUTBOL", documento="11365311")
        self.assertEqual(Equipo.objects.filter(nombre_club="REYES DEL FUTBOL").count(), 2)

    def test_saldo_factura(self):
        e = crear_equipo()
        f = Factura.objects.create(equipo=e, numero=58412, fecha=date(2026, 5, 27), valor_total=Decimal("1500000"))
        c = Cuota.objects.create(factura=f, numero=1, valor=Decimal("750000"), vencimiento=date(2026, 5, 27))
        Pago.objects.create(cuota=c, fecha=date(2026, 6, 1), valor=Decimal("750000"))
        self.assertEqual(f.numero_completo, "FV EF 58412")
        self.assertEqual(f.saldo, Decimal("750000"))

    def test_configuracion_unica_con_valores_del_excel(self):
        c = Configuracion.obtener()
        self.assertEqual(c.empresa, "INDEPENDIENTE SANTA FE S.A.")
        self.assertEqual(c.centro_costos, "9207 Copa Santa Fe equipos invitados")
        Configuracion(nombre_torneo="X").save()
        self.assertEqual(Configuracion.objects.count(), 1)


class VistasEquipoTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("tesoreria", password="clave-segura-123")
        self.client.login(username="tesoreria", password="clave-segura-123")

    def test_requiere_ingreso(self):
        self.client.logout()
        r = self.client.get(reverse("equipos:lista"))
        self.assertEqual(r.status_code, 302)

    def test_dashboard_y_lista(self):
        crear_equipo()
        self.assertContains(self.client.get(reverse("core:dashboard")), "Nuevo equipo")
        self.assertContains(self.client.get(reverse("equipos:lista")), "GIBOR FC")
        self.assertContains(self.client.get(reverse("equipos:lista"), {"q": "1000860"}), "GIBOR FC")
        self.assertNotContains(self.client.get(reverse("equipos:lista"), {"q": "zzz"}), "GIBOR FC</a>")

    def test_crear_equipo_registra_auditoria(self):
        r = self.client.post(reverse("equipos:crear"), {
            "nombre_club": "Funza FC", "razon_social": "Sebastian Puentes Triana", "documento": "1073237758",
            "valor": "1500000", "cuotas": "2", "descuentos": "0", "seguimiento": "Facturado",
        })
        e = Equipo.objects.get()
        self.assertRedirects(r, e.get_absolute_url())
        self.assertEqual(e.nombre_club, "FUNZA FC")
        self.assertTrue(RegistroAuditoria.objects.filter(accion="crear_equipo", usuario=self.usuario).exists())

    def test_no_permite_duplicado(self):
        crear_equipo()
        r = self.client.post(reverse("equipos:crear"), {
            "nombre_club": "gibor fc", "razon_social": "X", "documento": "1000860202",
            "valor": "1", "cuotas": "2", "descuentos": "0", "seguimiento": "Facturado",
        })
        self.assertContains(r, "Ya existe el equipo")
        self.assertEqual(Equipo.objects.count(), 1)

    def test_editar_y_desactivar(self):
        e = crear_equipo()
        self.client.post(reverse("equipos:editar", args=[e.pk]), {
            "nombre_club": "GIBOR FC", "razon_social": "JOSE DAVID RIVEROS SANTA", "documento": "1000860202",
            "valor": "1500000", "cuotas": "2", "descuentos": "0", "seguimiento": "Facturado", "telefono": "3001234567",
        })
        self.client.post(reverse("equipos:cambiar_estado", args=[e.pk]))
        e.refresh_from_db()
        self.assertEqual(e.telefono, "3001234567")
        self.assertFalse(e.activo)
        self.assertEqual(RegistroAuditoria.objects.filter(objeto_id=str(e.pk)).count(), 2)
        self.assertContains(self.client.get(reverse("equipos:detalle", args=[e.pk])), "Historial")
