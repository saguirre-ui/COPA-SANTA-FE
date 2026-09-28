from django import forms

from .models import Equipo, normalizar_texto


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = [
            "nombre_club",
            "razon_social",
            "documento",
            "digito_verificacion",
            "valor",
            "cuotas",
            "descuentos",
            "seguimiento",
            "responsable",
            "correo",
            "telefono",
            "direccion",
        ]
        widgets = {
            "nombre_club": forms.TextInput(attrs={"autofocus": True, "placeholder": "Ej. GIBOR FC"}),
            "razon_social": forms.TextInput(attrs={"placeholder": "Persona o empresa a quien se factura"}),
            "documento": forms.TextInput(attrs={"inputmode": "numeric", "placeholder": "Ej. 901809225"}),
            "digito_verificacion": forms.TextInput(attrs={"inputmode": "numeric", "maxlength": 1, "class": "input-dv"}),
            "valor": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "cuotas": forms.NumberInput(attrs={"min": 1, "max": 12}),
            "descuentos": forms.NumberInput(attrs={"min": 0, "step": 1}),
            "correo": forms.EmailInput(attrs={"placeholder": "tesoreria@club.com"}),
        }

    def clean_documento(self):
        return "".join(ch for ch in self.cleaned_data["documento"] if ch.isdigit())

    def clean(self):
        datos = super().clean()
        club = normalizar_texto(datos.get("nombre_club", ""))
        documento = datos.get("documento")
        if club and documento:
            repetido = Equipo.objects.filter(nombre_club=club, documento=documento)
            if self.instance.pk:
                repetido = repetido.exclude(pk=self.instance.pk)
            if repetido.exists():
                raise forms.ValidationError(
                    f"Ya existe el equipo {club} con el documento {documento}. Búsquelo en la lista y edítelo."
                )
        valor, descuentos = datos.get("valor"), datos.get("descuentos")
        if valor is not None and descuentos is not None and descuentos > valor:
            self.add_error("descuentos", "El descuento no puede ser mayor que el valor.")
        return datos
