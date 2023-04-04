from django import paymentstatus

register = paymentstatus.Library()

@register.filter
def divide_by_100(value):
    return float(value) / 100