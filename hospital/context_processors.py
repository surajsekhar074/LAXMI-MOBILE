# context_processors.py


from .models import Note

def admin_notifications(request):
    if request.user.is_authenticated and request.user.is_staff:
        notes = Note.objects.all().order_by('-created_at')
        return {'notifications': notes}
    return {'notifications': []}

from .models import Note

def notifications(request):
    if request.user.is_authenticated and request.user.is_staff:
        notes = Note.objects.all().order_by('-created_at')
        return {'notifications': notes}
    return {'notifications': []}


from .models import Store

def store_list(request):
    stores = Store.objects.all()
    return {'stores': stores}



from .models import Note

def notification_count(request):
    if request.user.is_authenticated and request.user.is_staff:
        notifications = Note.objects.filter(seen=False)
        return {'notifications': notifications}
    return {'notifications': []}


