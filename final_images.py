import os
import django
import urllib.request
import ssl
from django.core.files.base import ContentFile
from duckduckgo_search import DDGS
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_vault.settings')
django.setup()

from cars.models import Car, CarImage

def get_ddg_image(query):
    try:
        results = DDGS().images(query, max_results=3, safesearch='off', size='Large')
        if results:
            return results[0]['image']
    except Exception as e:
        print(f"    DDG API ERROR: {e}")
    return None

def run():
    missing_cars = Car.objects.filter(images__isnull=True)
    print(f"Attempting to fetch {missing_cars.count()} images through DuckDuckGo...")
    
    for car in missing_cars:
        print(f"Fetching: {car.brand} {car.model}")
        query = f"{car.year} {car.brand} {car.model} official exterior front high res"
        
        url = get_ddg_image(query)
        if url:
            print(f"    Found URL: {url} -> Downloading...")
            try:
                # Add headers because some domains reject python user agents
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                    img_content = response.read()
                    img_name = f"ddg_{car.brand.lower().replace(' ', '_')}_{car.model.lower().replace(' ', '_')}.jpg"
                    car_img = CarImage(car=car, is_primary=True)
                    car_img.image.save(img_name, ContentFile(img_content), save=True)
                    print(f"    [SUCCESS] Saved as {img_name}")
            except Exception as e:
                print(f"    [DOWNLOAD ERROR] {url}: {e}")
        else:
            print(f"    [SKIPPED] No image found on DDG for {query}")
            
        time.sleep(2) # Safe delay between searches
        
if __name__ == '__main__':
    run()
