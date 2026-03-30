from django.db import models

class Car(models.Model):
    title = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    year = models.IntegerField()
    mileage = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    @property
    def get_badges(self):
        badges = []
        if self.price < 35000:
            badges.append({'text': '🔥 Great Deal', 'class': 'bg-danger'})
        if hasattr(self, 'specifications'):
            if 'electric' in self.specifications.fuel_type.lower():
                badges.append({'text': '⚡ EV', 'class': 'bg-success'})
            elif 'hybrid' in self.specifications.fuel_type.lower():
                badges.append({'text': '🌱 Hybrid', 'class': 'bg-success'})
            if self.specifications.safety_rating == 5:
                badges.append({'text': '🛡️ Top Safety', 'class': 'bg-info text-dark'})
        return badges

class CarSpecification(models.Model):
    car = models.OneToOneField(Car, on_delete=models.CASCADE, related_name='specifications')
    engine = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    mileage = models.CharField(max_length=50, help_text="e.g. 20 kmpl")
    safety_rating = models.IntegerField(help_text="Out of 5 stars", default=0)

    def __str__(self):
        return f"Specs for {self.car.title}"

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.car.title}"

class Accessory(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='accessories')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} for {self.car.title}"

class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars for {self.car.title} by {self.user.username}"
