from django import template

register = template.Library()

@register.filter
def indian_lakhs(value):
    try:
        val = float(value)
    except (ValueError, TypeError):
        return value
        
    if val >= 10000000:
        return f"{val/10000000:.2f} Cr".rstrip('0').rstrip('.')
    elif val >= 100000:
        return f"{val/100000:.2f} Lakh".rstrip('0').rstrip('.')
    else:
        return f"{val:,.0f}"
