import json
import urllib.request
import urllib.parse
import ssl
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from cars.models import Car, CarSpecification, CarImage

import os

class Command(BaseCommand):
    help = 'Seeds the database with real cars and fetches their images from Wikipedia.'
    help = 'Seeds the database with 15 real cars and fetches their images from Wikipedia.'

    def get_wiki_image(self, title):
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1000"
        headers = {'User-Agent': 'VehicleVault/1.0 (kriyank@example.com)'}
        req = urllib.request.Request(url, headers=headers)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode())
                pages = data.get('query', {}).get('pages', {})
                for page_id, info in pages.items():
                    if 'thumbnail' in info:
                        return info['thumbnail']['source']
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not fetch wiki image for {title}: {e}"))
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting existing cars to reset images...")
        Car.objects.all().delete()
        
        self.stdout.write("Seeding cars...")
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        json_path = os.path.join(os.path.dirname(__file__), 'indian_cars_data.json')
        with open(json_path, 'r') as f:
            cars_data = json.load(f)

        for data in cars_data:
            car, created = Car.objects.get_or_create(
                title=data['title'],
                defaults={
                    'brand': data['brand'],
                    'model': data['model'],
                    'price': data['price'],
                    'year': data['year'],
                    'mileage': data['mileage'],
                    'description': data['description']
                }
            )
            
            if created:
                # Add specs
                CarSpecification.objects.create(
                    car=car,
                    engine=data['engine'],
                    fuel_type=data['fuel_type'],
                    transmission=data['transmission'],
                    mileage="See EV range/MPG", 
                    safety_rating=data['safety']
                )
                
                # Fetch and add image
                img_url = self.get_wiki_image(data['wiki'])
                if img_url:
                    self.stdout.write(f"Downloading image for {car.title}...")
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    try:
                        import time
                        time.sleep(1.5)
                        with urllib.request.urlopen(req, context=ctx) as response:
                            img_content = response.read()
                            img_name = f"{car.brand.lower().replace(' ', '_')}_{car.model.lower().replace(' ', '_')}.jpg"
                            car_image = CarImage(car=car, is_primary=True)
                            car_image.image.save(img_name, ContentFile(img_content), save=True)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to download image for {car.title}: {e}"))
                self.stdout.write(self.style.SUCCESS(f"Added {car.title}"))
            else:
                self.stdout.write(f"{car.title} already exists. Skipping.")
                
        self.stdout.write(self.style.SUCCESS(f"Database perfectly seeded with {len(cars_data)} Indian market cars!"))
