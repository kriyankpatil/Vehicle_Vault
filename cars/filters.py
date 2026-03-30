import django_filters
from django import forms
from .models import Car

def get_brand_choices():
    try:
        brands = Car.objects.values_list('brand', flat=True).distinct().order_by('brand')
        return [(brand, brand) for brand in brands]
    except Exception:
        return []

class CarFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte', label='Min Price')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte', label='Max Price')
    brand = django_filters.ChoiceFilter(field_name='brand', choices=get_brand_choices, label='Brand', widget=forms.Select(attrs={'class': 'form-select'}))
    year = django_filters.NumberFilter(field_name='year', label='Year')
    fuel_type = django_filters.CharFilter(field_name='specifications__fuel_type', lookup_expr='icontains', label='Fuel Type')
    transmission = django_filters.CharFilter(field_name='specifications__transmission', lookup_expr='icontains', label='Transmission')

    class Meta:
        model = Car
        fields = ['brand', 'year']
