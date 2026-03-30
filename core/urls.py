from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('smart-match/', views.SmartMatchView.as_view(), name='smart_match'),
    path('analytics/', views.AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('api/chatbot/', views.ChatbotAPIView.as_view(), name='api_chatbot'),
    path('activate/<uidb64>/<token>/', views.ActivateView.as_view(), name='activate'),
]
