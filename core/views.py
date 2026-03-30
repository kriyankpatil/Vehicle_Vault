from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from cars.models import Car
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from .models import UserProfile
from django.contrib.auth.models import User

class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get 6 latest cars to show as featured
        context['featured_cars'] = Car.objects.all().order_by('-created_at')[:6]
        return context

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password')
        )
        
        if user is not None:
            # Check if email is verified
            if not user.profile.is_email_verified:
                messages.error(self.request, "Your email is not verified. Please check your inbox for the activation link.")
                return self.form_invalid(form)
                
        # Capture anonymous session key
        old_session_key = self.request.session.session_key
        
        # Super logs them in, generating new session_key
        response = super().form_valid(form)
        new_session_key = self.request.session.session_key
        
        if old_session_key and new_session_key and old_session_key != new_session_key:
            from favorites.models import Favorite
            from comparisons.models import Comparison
            Favorite.objects.filter(session_id=old_session_key).update(session_id=new_session_key)
            Comparison.objects.filter(session_id=old_session_key).update(session_id=new_session_key)
            
        return response

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        
        # Stop auto-login after registration
        # Instead, send verification email
        current_site = get_current_site(self.request)
        subject = 'Activate Your Vehicle Vault Account'
        message = render_to_string('registration/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        
        send_mail(subject, message, None, [user.email])
        
        # Note: We don't call login(self.request, user) here
        return render(self.request, 'registration/activation_sent.html')

from django.views import View
from django.shortcuts import redirect, render
import urllib.parse

class ActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.profile.is_email_verified = True
            user.profile.save()
            return render(request, 'registration/activation_success.html')
        else:
            return render(request, 'registration/activation_invalid.html')

class SmartMatchView(View):
    def get(self, request):
        return render(request, 'core/smart_match.html')
        
    def post(self, request):
        budget = request.POST.get('budget', '')
        fuel = request.POST.get('fuel', '')
        priority = request.POST.get('priority', '')
        
        # Build query string for CarListView
        params = {}
        
        if budget == 'under_15':
            params['max_price'] = '1500000'
        elif budget == 'under_25':
            params['max_price'] = '2500000'
        elif budget == 'under_50':
            params['max_price'] = '5000000'
            
        if fuel != 'any':
            params['fuel_type'] = fuel
            
        # For priority, we'll map to a custom sort parameter which we will add to CarListView
        if priority == 'safety':
            params['sort'] = 'safety_desc'
        elif priority == 'performance':
            params['sort'] = 'performance'
        elif priority == 'value':
            params['sort'] = 'price_asc'
            
        query_string = urllib.parse.urlencode(params)
        return redirect(f"/cars/?{query_string}")

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Avg
from django.http import JsonResponse
import json

from django.core.serializers.json import DjangoJSONEncoder

class AnalyticsDashboardView(UserPassesTestMixin, TemplateView):
    template_name = "core/dashboard.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cars = Car.objects.all()
        
        # 1. Price vs Brand
        brands = cars.values('brand').annotate(avg_price=Avg('price'), count=Count('id')).order_by('-count')
        context['brand_stats'] = json.dumps(list(brands), cls=DjangoJSONEncoder)
        
        # 2. Fuel Type Distribution
        fuel_types = cars.values('specifications__fuel_type').annotate(count=Count('id'))
        # Normalize simple fuel types roughly (e.g. Petrol / CNG -> Petrol)
        fuel_map = {}
        for f in fuel_types:
            name = f['specifications__fuel_type']
            if not name: continue
            if 'Petrol' in name: key = 'Petrol'
            elif 'Diesel' in name: key = 'Diesel'
            elif 'Electric' in name: key = 'Electric'
            elif 'Hybrid' in name: key = 'Hybrid'
            elif 'CNG' in name: key = 'CNG'
            else: key = 'Other'
            fuel_map[key] = fuel_map.get(key, 0) + f['count']
        
        context['fuel_stats'] = json.dumps([{'label': k, 'count': v} for k, v in fuel_map.items()])
        context['total_cars'] = cars.count()
        context['avg_cost'] = cars.aggregate(Avg('price'))['price__avg'] or 0
        return context

class ChatbotAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            query = data.get('message', '').lower()
        except Exception:
            return JsonResponse({'reply': "I didn't understand that. Try 'suggest an electric car' or 'suv under 15 lakhs'."})
            
        cars = Car.objects.all()
        reply_prefix = "Sure thing! "
        
        if 'electric' in query or 'ev' in query:
            cars = cars.filter(specifications__fuel_type__icontains='Electric')
            reply_prefix = "Here are some futuristic EVs you might like: "
        elif 'hybrid' in query:
            cars = cars.filter(specifications__fuel_type__icontains='Hybrid')
            reply_prefix = "Here are some excellent hybrid options: "
        elif 'diesel' in query:
            cars = cars.filter(specifications__fuel_type__icontains='Diesel')
            
        if 'suv' in query:
            cars = cars.filter(title__icontains='suv') | cars.filter(description__icontains='suv')
            reply_prefix = "SUVs are perfect for Indian roads. Check these out: "
        elif 'sedan' in query:
            cars = cars.filter(description__icontains='sedan')
            
        # Very rough price parsing (e.g., "under 15 lakh", "under 20 lakh")
        import re
        match = re.search(r"under (\d+)", query)
        if match:
            lakhs = int(match.group(1))
            limit = lakhs * 100000
            cars = cars.filter(price__lte=limit)
            reply_prefix += f"I found some great cars under {lakhs} Lakhs: "
            
        # Sort by popularity roughly (using id as dummy sort)
        suggestions = cars.order_by('?')[:3]
        
        if suggestions.exists():
            car_links = []
            for c in suggestions:
                val = float(c.price)
                if val >= 10000000:
                    disp = f"{val/10000000:.2f} Cr".rstrip('0').rstrip('.')
                elif val >= 100000:
                    disp = f"{val/100000:.2f} Lakh".rstrip('0').rstrip('.')
                else:
                    disp = f"{val:,.0f}"
                car_links.append(f"<a href='/cars/{c.id}/'><b>{c.title}</b> (₹{disp})</a>")
            reply = reply_prefix + "<br>• " + "<br>• ".join(car_links)
        else:
            reply = "I couldn't find any perfect matches for that locally. Want to try another search?"
            
        return JsonResponse({'reply': reply})
