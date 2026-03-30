from django.db import models
from cars.models import Car

class Favorite(models.Model):
    session_id = models.CharField(max_length=255)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_id', 'car')

    def __str__(self):
        return f"{self.car.title} in session {self.session_id}"
