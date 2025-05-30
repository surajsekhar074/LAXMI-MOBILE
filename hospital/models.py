from django.db import models
from django.contrib.auth.models import User

# Store model
class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    worker = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_store')

    def __str__(self):
        return self.name

# Stock model
class Stock(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)


    wehave = models.IntegerField(default=0)
    contact = models.IntegerField(default=0)
    sold_today = models.IntegerField(default=0)

    system = models.IntegerField()
    remaining = models.IntegerField()

    review1 = models.IntegerField(default=0)  # abc - system
    review2 = models.IntegerField(default=0)  # abc - remaining
    stock_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    
  

    def __str__(self):
        return f"Stock on {self.date}"

# Worker profile
class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

from django.contrib.auth.models import User

class Note(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='notes')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    problem = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)  # 👈 NEW FIELD

    def __str__(self):
        return f"{self.model_name} - {self.problem[:20]}"
