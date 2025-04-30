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
from django.contrib.auth.models import User
from django.contrib.auth import login

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
        total_contact=Sum('contact'),
        total_sold=Sum('sold_today'),
        total_remaining=Sum('remaining'),
        total_review=Sum('review')
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
@login_required
def add_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # Get yesterday's stock entry if available, otherwise default to 0
    yesterday_stock = Stock.objects.filter(store=store).order_by('-date').first()
    yesterday_remaining = yesterday_stock.remaining if yesterday_stock else 0

    if request.method == 'POST':
        # Get values from the submitted form
        date = request.POST.get('date')
        contact = int(request.POST.get('contact'))
        sold_today = int(request.POST.get('sold_today'))
        system = int(request.POST.get('system'))  # Convert to int

        wehave = yesterday_remaining
        review = wehave - system  # This is now safe
        remaining = wehave + contact - sold_today

        # Save the stock entry
        Stock.objects.create(
            store=store,
            date=date,
            wehave=wehave,
            system=system,
            contact=contact,
            sold_today=sold_today,
            remaining=remaining,
            review=review
        )

        return redirect('store_stock_view', store_id=store.id)

    return render(request, 'add_stock.html', {
        'store': store,
        'yesterday_remaining': yesterday_remaining,
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



















