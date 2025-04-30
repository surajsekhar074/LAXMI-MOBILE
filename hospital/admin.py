from django.contrib import admin
from .models import Stock
from .models import Store
from .models import WorkerProfile

# Register your models here.


admin.site.register(Store)
admin.site.register(Stock)



admin.site.register(WorkerProfile)





