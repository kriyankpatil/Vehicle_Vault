from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import DetailView
from django_filters.views import FilterView
from .models import Car
from .filters import CarFilter
from .forms import ReviewForm

class CarListView(FilterView):
    model = Car
    context_object_name = 'cars'
    filterset_class = CarFilter
    paginate_by = 12

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ['partials/car_grid.html']
        return ['cars/car_list.html']

    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            return qs.order_by('price')
        elif sort == 'price_desc':
            return qs.order_by('-price')
        elif sort == 'year_desc':
            return qs.order_by('-year')
        elif sort == 'year_asc':
            return qs.order_by('year')
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = self.request.session.session_key
        if not session_id:
            self.request.session.save()
            session_id = self.request.session.session_key
        context['session_id'] = session_id
        return context

class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'
    context_object_name = 'car'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_cars'] = Car.objects.filter(brand=self.object.brand).exclude(id=self.object.id)[:4]
        context['review_form'] = ReviewForm()
        # Ensure we display average rating
        reviews = self.object.reviews.all()
        if reviews.exists():
            context['avg_rating'] = sum([r.rating for r in reviews]) / reviews.count()
        else:
            context['avg_rating'] = 0
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect('login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.car = self.object
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been verified and posted!")
            return redirect('cars:car_detail', pk=self.object.pk)
            
        context = self.get_context_data()
        context['review_form'] = form
        return self.render_to_response(context)

from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from django.shortcuts import get_object_or_404, render

class CarPDFExportView(View):
    def get(self, request, pk, *args, **kwargs):
        car = get_object_or_404(Car, pk=pk)
        template_path = 'cars/pdf_quotation.html'
        
        context = {
            'car': car,
            'specs': car.specifications if hasattr(car, 'specifications') else None,
            'base_price': car.price,
            'insurance_estimate': float(car.price) * 0.04,
        }
        
        return render(request, template_path, context)
