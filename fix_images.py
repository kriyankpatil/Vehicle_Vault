import os
import django
import json
import urllib.request
import urllib.parse
import ssl
import time
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_vault.settings')
django.setup()

from cars.models import Car, CarImage
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'VehicleVaultImageFixer/1.0 (contact@example.com)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
]

def get_wiki_image(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=1000"
    headers = {'User-Agent': random.choice(USER_AGENTS)}
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
        print(f"  [API Error] Could not fetch wiki image for {title}: {e}")
    return None

def run():
    cars_without_images = Car.objects.filter(images__isnull=True)
    print(f"Found {cars_without_images.count()} cars without images.")
    
    if cars_without_images.count() == 0:
        return
        
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # We will search the indian_cars_data to match the wiki slug
    with open('cars/management/commands/indian_cars_data.json', 'r') as f:
        cars_data = json.load(f)
        
    slug_map = {c['title']: c['wiki'] for c in cars_data}
    
    for car in cars_without_images:
        wiki_slug = slug_map.get(car.title)
        if not wiki_slug:
            wiki_slug = f"{car.brand.replace(' ', '_')}_{car.model.replace(' ', '_')}"
            
        print(f"Attempting to fetch image for: {car.title} (slug: {wiki_slug})")
        time.sleep(2.5) # generous sleep to avoid 429
        
        img_url = get_wiki_image(wiki_slug)
        if img_url:
            print(f"  Found image URL! Downloading...")
            req = urllib.request.Request(img_url, headers={'User-Agent': random.choice(USER_AGENTS)})
            try:
                time.sleep(1)
                with urllib.request.urlopen(req, context=ctx) as response:
                    img_content = response.read()
                    img_name = f"{car.brand.lower().replace(' ', '_')}_{car.model.lower().replace(' ', '_')}_fixed.jpg"
                    car_image = CarImage(car=car, is_primary=True)
                    car_image.image.save(img_name, ContentFile(img_content), save=True)
                    print(f"  [SUCCESS] Downloaded and saved {img_name}")
            except Exception as e:
                print(f"  [ERROR] Failed to download image file: {e}")
        else:
            print(f"  [SKIPPED] No image found on Wikipedia for {wiki_slug}")

if __name__ == '__main__':
    run()
