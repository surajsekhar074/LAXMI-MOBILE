from django.core.cache import cache
from django.utils import timezone

def save_note_to_cache(note_text, user):
    if not note_text.strip():
        return

    # Create a unique key for each note using the current timestamp
    key = f'note_{timezone.now().timestamp()}'
    expiry = 60 * 60 * 24  # 24 hours

    # Store the note with its data (user, note content, time)
    note_data = {
        'user': user.username,
        'note': note_text.strip(),
        'time': timezone.now().strftime("%Y-%m-%d %H:%M"),
    }

    # Save the note data to cache
    cache.set(key, note_data, timeout=expiry)

    # Add this note key to the list of notes
    note_list = cache.get('note_list') or []
    note_list.append(key)
    cache.set('note_list', note_list, timeout=expiry)
