from django.core.cache import cache

def admin_notifications(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    notes = []
    note_keys = cache.get("note_list", [])

    for key in note_keys:
        note = cache.get(key)
        if note:
            notes.append(note)

    return {"admin_notes": notes}



from django.core.cache import cache

def admin_notifications(request):
    # Get the list of all note keys from cache
    note_list = cache.get('note_list', [])
    
    # Fetch each note's data
    notifications = [cache.get(note_key) for note_key in note_list]
    
    # Only show notifications that have not expired (after 24 hours)
    notifications = [note for note in notifications if note and note.get('time')]
    
    # Return notifications to the template
    return {
        'notifications': notifications
    }



def get_notifications(request):
    note_list = cache.get('note_list', [])
    notifications = []
    
    # Fetch note data for each key in the list
    for note_key in note_list:
        note_data = cache.get(note_key)
        if note_data:
            notifications.append(note_data)
    
    return {'notifications': notifications}




from .models import Store

def store_list(request):
    stores = Store.objects.all()
    return {'stores': stores}

