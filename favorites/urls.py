from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.FavoriteListView.as_view(), name='favorite_list'),
    path('toggle/<int:car_id>/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
]
