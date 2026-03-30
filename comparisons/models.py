from django.db import models
from cars.models import Car

class Comparison(models.Model):
    session_id = models.CharField(max_length=255)
    car_1 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='comparisons_as_car1', null=True)
    car_2 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='comparisons_as_car2', null=True, blank=True)
    car_3 = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='comparisons_as_car3', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison session: {self.session_id}"

    class Meta:
        # A single session should have one active comparison row
        unique_together = ('session_id',)
