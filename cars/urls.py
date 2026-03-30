from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.CarListView.as_view(), name='car_list'),
    path('<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('<int:pk>/pdf/', views.CarPDFExportView.as_view(), name='car_pdf_export'),
]
