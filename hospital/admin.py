from django.contrib import admin
from .models import Stock
from .models import Store
from .models import WorkerProfile
from .models import Note
from .models import StockTransfer
# Register your models here.


admin.site.register(Store)
admin.site.register(Stock)



admin.site.register(WorkerProfile)


admin.site.register(Note)
admin.site.register(StockTransfer)







