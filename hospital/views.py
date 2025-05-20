from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.urls import re_path as login
from django.urls import re_path as authenticate
from django.http import HttpResponseServerError
from django.contrib.auth import logout 
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import render
from .models import Store
from django.contrib.auth import authenticate, login
from .models import WorkerProfile
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.shortcuts import render, get_object_or_404
from .models import Store, Stock
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from datetime import date
from django.contrib.auth.models import User
# assuming you link users to stores





# Create your views here.




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def Login(request):
    error = ""  # To store error messages
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            return redirect('home')  # Redirect to your index view
        else:
            error = "yes"
    
    return render(request, 'login.html', {'error': error})



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def logout_Admin(request):
    # if not request.user.is_staff:
    #     return redirect('login')\
    request.session.clear()
    logout(request)
    return redirect('login')



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if hasattr(user, 'workerprofile'):
                store = user.workerprofile.store
                return redirect('store_stock_view', store_id=store.id)
            else:
                # Admin or staff user – redirect to dashboard or homepage
                return redirect('home')  # or your custom admin dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

   
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@login_required
def index(request):
    stores = Store.objects.all()

    store_id = request.GET.get('store_id')
    selected_date = request.GET.get('date')

    stocks = Stock.objects.all()

    if store_id:
        stocks = stocks.filter(store_id=store_id)
    
    if selected_date:
        selected_date = parse_date(selected_date)
        stocks = stocks.filter(date=selected_date)

    # Now do the aggregation based on the filtered stocks
    totals = stocks.aggregate(
        total_wehave=Sum('wehave'),
        total_system=Sum('system'),
        total_contact=Sum('contact'),  total_sold=Sum('sold_today'),
        total_remaining=Sum('remaining'),
        total_review1=Sum('review1'),
        total_review2=Sum('review2')
    )

    context = {
        'stores': stores,
        'totals': totals,
    }
    return render(request, 'index.html', context)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@login_required
def store_stock_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    
    # Get the stock records for the store, ordered by date (newest first)
    stock_records = Stock.objects.filter(store=store).order_by('-date')
    
    return render(request, 'store_stock_view.html',  {'store': store, 'stock_records': stock_records})



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@login_required
def register_store(request):
    if request.method == 'POST':
        name = request.POST['name']
        location = request.POST.get('location', '')

        store = Store.objects.create(name=name, location=location)

        # Redirect to the index page after registration
        return redirect('home')  # Adjust this to your index URL name
    return render(request, 'store_registrations.html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


from django.shortcuts import get_object_or_404, render, redirect
from .models import Store, Stock
from .utils import save_note_to_cache
from datetime import date
from django.contrib.auth.decorators import login_required

@login_required
def add_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    yesterday_stock = Stock.objects.filter(store=store).order_by('-date').first()
    yesterday_remaining = yesterday_stock.remaining if yesterday_stock else 0
    today = date.today().isoformat()

    if request.method == 'POST':
        form_date = request.POST.get('date')
        contact = int(request.POST.get('contact'))
        sold_today = int(request.POST.get('sold_today'))
        entered_remaining = int(request.POST.get('remaining'))
        system = int(request.POST.get('system'))
        note = request.POST.get('note', '').strip()

        # Use yesterday's remaining as opening stock
        wehave = yesterday_remaining

        # Calculate abc
        abc = wehave + contact - sold_today

        # Calculate review1 and review2
        review1 = abc - system
        review2 = abc - entered_remaining

        # Save note if present
        if note:
            save_note_to_cache(note, request.user)

        # Save the stock entry with both review values
        Stock.objects.create(
            store=store,
            date=form_date,
            wehave=wehave,
            contact=contact,
            sold_today=sold_today,
            system=system,
            remaining=entered_remaining,
            
            review1=review1,
            review2=review2
            
        )

        return redirect('store_stock_view', store_id=store.id)

    return render(request, 'add_stock.html', {
        'store': store,
        'yesterday_remaining': yesterday_remaining,
        'today': today,
    })








      




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@login_required
def admin_add_user(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.create_user(username=username, password=password)
        store.worker = user
        store.save()

        return redirect('home')  # adjust as needed

    return render(request, 'admin_add_user.html', {'store': store})

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@login_required
def redirect_to_store_stock(request):
    try:
        store = request.user.assigned_store
        return redirect('store_stock_view', store_id=store.id)
    except:
        return redirect('no_store_assigned')  # fallback if no store is assigned

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_user_to_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    error_message = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            error_message = "Username already exists. Please choose a different one."
        else:
            try:
                user = User.objects.create_user(username=username, password=password)
                WorkerProfile.objects.create(user=user, store=store)
                return redirect('home')  # or wherever
            except IntegrityError:
                error_message = "An unexpected error occurred. Try again."

    return render(request, 'admin_add_user.html', {'store': store, 'error_message': error_message})

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~











from django.core.cache import cache
import uuid
from datetime import timedelta

def save_user_note(request):
    if request.method == 'POST':
        note_text = request.POST.get('note')
        user = request.user

        if note_text:
            key = f"note_{uuid.uuid4()}"
            note_data = {
                'user': user.username,
                'note': note_text,
            }

            # Save note in cache for 24 hours
            cache.set(key, note_data, timeout=86400)  # 24 hrs

            # Track all note keys
            existing_keys = cache.get('note_list') or []
            existing_keys.append(key)
            cache.set('note_list', existing_keys, timeout=86400)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone




def notifications_view(request):
    note_list = cache.get('note_list', [])
    notifications = []
    
    for note_key in note_list:
        note_data = cache.get(note_key)
        if note_data:
            notifications.append(note_data)
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
    })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def all_users_view(request):
    users = User.objects.all().select_related('assigned_store')
    return render(request, 'all_users.html', {'users': users})





from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import WorkerProfile

@login_required
def all_users_view(request):
    users = WorkerProfile.objects.select_related('user', 'store').all()
    return render(request, 'all_users.html', {'users': users}) 





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import WorkerProfile, Store
from django.contrib import messages

def all_users_view(request):
    users = WorkerProfile.objects.select_related('user', 'store')
    return render(request, 'all_users.html', {'users': users})

def reset_password_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        user.set_password(new_password)
        user.save()
        messages.success(request, f"Password reset for {user.username}")
        return redirect('all_users')
    return render(request, 'reset_password.html', {'user': user})

def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(WorkerProfile, user=user)

    if request.method == 'POST':
        username = request.POST.get('username')
        store_id = request.POST.get('store')
        user.username = username
        user.save()
        profile.store = Store.objects.get(id=store_id)
        profile.save()
        messages.success(request, "User updated successfully.")
        return redirect('all_users')

    stores = Store.objects.all()
    return render(request, 'edit_user.html', {'user': user, 'profile': profile, 'stores': stores})

def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('all_users')
    return render(request, 'confirm_delete.html', {'user': user})







from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

def create_superuser_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        User = get_user_model()
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email='', password=password)
            print(f"Superuser {username} created")  # Debug line
            return redirect('login')  # Make sure 'login' URL name exists
        else:
            context = {'error': 'User already exists'}
            return render(request, 'create_superuser.html', context)
    return render(request, 'create_superuser.html')
















