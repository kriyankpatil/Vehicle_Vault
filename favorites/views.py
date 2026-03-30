from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib import messages
from cars.models import Car
from .models import Favorite

class ToggleFavoriteView(View):
    def post(self, request, car_id):
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        car = get_object_or_404(Car, id=car_id)
        fav, created = Favorite.objects.get_or_create(session_id=session_id, car=car)
        
        if not created:
            fav.delete()
            messages.info(request, "Removed from favorites.")
        else:
            messages.success(request, "Added to favorites.")
            
        return redirect(request.META.get('HTTP_REFERER', 'cars:car_list'))

class FavoriteListView(ListView):
    model = Favorite
    template_name = 'favorites/favorite_list.html'
    context_object_name = 'favorites'
    paginate_by = 12

    def get_queryset(self):
        if not self.request.session.session_key:
            return Favorite.objects.none()
        return Favorite.objects.filter(session_id=self.request.session.session_key).order_by('-created_at')
