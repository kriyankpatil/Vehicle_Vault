from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from cars.models import Car
from .models import Comparison

class AddCompareView(View):
    def post(self, request, car_id):
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        
        car = get_object_or_404(Car, id=car_id)
        comp, created = Comparison.objects.get_or_create(session_id=session_id)
        
        # Check if already added
        if comp.car_1 == car or comp.car_2 == car or comp.car_3 == car:
            messages.info(request, "Car is already in comparison.")
            return redirect(request.META.get('HTTP_REFERER', 'cars:car_list'))

        # Add to first empty slot
        if not comp.car_1:
            comp.car_1 = car
        elif not comp.car_2:
            comp.car_2 = car
        elif not comp.car_3:
            comp.car_3 = car
        else:
            messages.warning(request, "You can only compare up to 3 cars at a time.")
            return redirect(request.META.get('HTTP_REFERER', 'cars:car_list'))
            
        comp.save()
        messages.success(request, f"{car.brand} {car.model} added to comparison.")
        return redirect(request.META.get('HTTP_REFERER', 'cars:car_list'))

class RemoveCompareView(View):
    def post(self, request, car_id):
        session_id = request.session.session_key
        if not session_id:
            return redirect('cars:car_list')
        
        comp = Comparison.objects.filter(session_id=session_id).first()
        if comp:
            car = get_object_or_404(Car, id=car_id)
            if comp.car_1 == car:
                comp.car_1 = None
            elif comp.car_2 == car:
                comp.car_2 = None
            elif comp.car_3 == car:
                comp.car_3 = None
            comp.save()
            # Clean up empty slots (compacting)
            cars = [c for c in [comp.car_1, comp.car_2, comp.car_3] if c]
            comp.car_1 = cars[0] if len(cars) > 0 else None
            comp.car_2 = cars[1] if len(cars) > 1 else None
            comp.car_3 = cars[2] if len(cars) > 2 else None
            comp.save()
            messages.success(request, "Car removed from comparison.")
        
        return redirect(request.META.get('HTTP_REFERER', 'comparisons:compare_table'))

class ComparisonTableView(TemplateView):
    template_name = 'comparisons/compare_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.session.session_key:
            self.request.session.create()
        session_id = self.request.session.session_key
        
        comp = Comparison.objects.filter(session_id=session_id).first()
        cars = []
        if comp:
            if comp.car_1: cars.append(comp.car_1)
            if comp.car_2: cars.append(comp.car_2)
            if comp.car_3: cars.append(comp.car_3)
            
        context['cars'] = cars
        
        if cars:
            context['best_price'] = min(cars, key=lambda c: c.price).price
            
            # Helper to safely get safety rating
            def get_safety(car):
                if hasattr(car, 'specifications') and car.specifications:
                    return car.specifications.safety_rating
                return 0
            
            context['best_safety'] = max(cars, key=get_safety)
            context['best_safety_val'] = get_safety(context['best_safety'])
            
            # We must pass the highest price to calculate progress bar width
            context['max_price'] = max(cars, key=lambda c: c.price).price
            
            # automated pros and cons
            for car in cars:
                car.pros = []
                car.cons = []

                if car.price == context['best_price']:
                    car.pros.append("Most affordable choice")
                elif car.price == context['max_price'] and len(cars) > 1:
                    car.cons.append("Most expensive option")

                if get_safety(car) == context['best_safety_val'] and context['best_safety_val'] > 0:
                    car.pros.append(f"Top Safety ({context['best_safety_val']} Stars)")
                elif get_safety(car) < 4:
                    car.cons.append(f"Lower safety rating ({get_safety(car)} Stars)")

                if hasattr(car, 'specifications') and car.specifications:
                    fuel = car.specifications.fuel_type.lower()
                    if 'electric' in fuel or 'ev' in fuel:
                        car.pros.append("Eco-friendly (Electric)")
                        car.cons.append("Dependent on charging infrastructure")
                    elif 'hybrid' in fuel:
                        car.pros.append("Excellent mileage (Hybrid)")
                        
                if car.year < 2020:
                    car.cons.append("Older model year")
                else:
                    car.pros.append("Modern technology & features")
                        
                # Fallbacks
                if not car.pros:
                    car.pros.append("Reliable manufacturer")
                if not car.cons:
                    car.cons.append("Higher maintenance cost")
            
        return context
