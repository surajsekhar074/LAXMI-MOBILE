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
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    wehave = models.IntegerField(default=0)
    contact = models.IntegerField()  # items added today
    sold_today = models.IntegerField(blank=True, null=True)

    remaining = models.IntegerField()
    review = models.IntegerField()  # remaining stock


    def save(self, *args, **kwargs):
        # Ensure the fields are integers (convert from strings if needed)
        self.wehave = int(self.wehave) if not isinstance(self.wehave, int) else self.wehave
        self.contact = int(self.contact) if not isinstance(self.contact, int) else self.contact
        self.sold_today = int(self.sold_today) if self.sold_today is not None and not isinstance(self.sold_today, int) else self.sold_today
        
        # Calculate remaining stock
        self.remaining = self.wehave + self.contact - (self.sold_today or 0)
        
        # Save the instance
        super(Stock, self).save(*args, **kwargs)



    def __str__(self):
        return f"Stock on {self.date}"
    



from django.contrib.auth.models import User
from django.db import models
class WorkerProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


    

