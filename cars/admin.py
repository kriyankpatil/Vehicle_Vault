from django.contrib import admin
from .models import Car, CarSpecification, CarImage, Accessory

class CarSpecificationInline(admin.StackedInline):
    model = CarSpecification

class CarImageInline(admin.TabularInline):
    model = CarImage

class AccessoryInline(admin.TabularInline):
    model = Accessory

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'model', 'year', 'price')
    list_filter = ('brand', 'year')
    search_fields = ('title', 'brand', 'model')
    inlines = [CarSpecificationInline, CarImageInline, AccessoryInline]

admin.site.register(CarSpecification)
admin.site.register(CarImage)
admin.site.register(Accessory)
