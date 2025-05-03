from django.db import models
from django.contrib.auth.models import User

# Create your models here.


from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    worker = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_store')

    def __str__(self):
        return self.name







class Stock(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    wehave = models.IntegerField(default=0)
    contact = models.IntegerField(default=0)
    sold_today = models.IntegerField(default=0)

    system = models.IntegerField()
    remaining = models.IntegerField()

    review1 = models.IntegerField(default=0)  # abc - system
    review2 = models.IntegerField(default=0)  # abc - remaining

    def __str__(self):
        return f"Stock on {self.date}"


    



from django.contrib.auth.models import User
from django.db import models
class WorkerProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


    

