from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def pesos(valor):
    """1500000 -> $ 1.500.000 (formato colombiano)."""
    try:
        numero = Decimal(valor or 0)
    except (InvalidOperation, TypeError):
        return valor
    signo = "-" if numero < 0 else ""
    return f"{signo}$ {abs(numero):,.0f}".replace(",", ".")
