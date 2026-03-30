from django.urls import path
from . import views

app_name = 'comparisons'

urlpatterns = [
    path('', views.ComparisonTableView.as_view(), name='compare_table'),
    path('add/<int:car_id>/', views.AddCompareView.as_view(), name='add_compare'),
    path('remove/<int:car_id>/', views.RemoveCompareView.as_view(), name='remove_compare'),
]
