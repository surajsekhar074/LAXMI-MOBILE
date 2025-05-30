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

import json
from django.utils.dateparse import parse_date
from django.db.models import Sum
from decimal import Decimal

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

    # Aggregation for totals
    totals = stocks.aggregate(
        total_wehave=Sum('wehave'),
        total_system=Sum('system'),
        total_contact=Sum('contact'),
        total_sold=Sum('sold_today'),
        total_remaining=Sum('remaining'),
        total_review1=Sum('review1'),
        total_review2=Sum('review2'),
        total_stock_value=Sum('stock_value')
    )

    # Prepare last 7 days stock_value data for chart
    import datetime
    from django.utils.timezone import now

    today = now().date()
    last_7_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]  # oldest to newest

    # Filter stocks for last 7 days and optional store filter
    last_7_days_stocks = Stock.objects.filter(date__in=last_7_days)
    if store_id:
        last_7_days_stocks = last_7_days_stocks.filter(store_id=store_id)

    # Aggregate stock_value by date
    stock_values_qs = last_7_days_stocks.values('date').annotate(total_value=Sum('stock_value'))

    # Build a dict for quick lookup
    values_dict = {item['date']: item['total_value'] for item in stock_values_qs}

    stock_value_data = []
    for day in last_7_days:
        value = values_dict.get(day, 0) or 0
        # Convert Decimal to float
        if isinstance(value, Decimal):
            value = float(value)
        stock_value_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'value': value,
        })

    context = {
        'stores': stores,
        'totals': totals,
        'stock_value_data': json.dumps(stock_value_data),  # JSON string
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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from .models import Store, Stock, Note

@login_required
def add_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    today = date.today()
    yesterday = today - timedelta(days=1)

    previous_stock = Stock.objects.filter(store=store, date=yesterday).first()
    yesterday_remaining = previous_stock.remaining if previous_stock else 0

    if request.method == 'POST':
        # Get form data
        contact = int(request.POST.get('contact') or 0)
        sold_today = int(request.POST.get('sold_today') or 0)
        remaining = int(request.POST.get('remaining') or 0)
        system = int(request.POST.get('system') or 0)

        try:
            stock_value = Decimal(request.POST.get('stock_value') or '0')
        except InvalidOperation:
            stock_value = Decimal('0')

        wehave = yesterday_remaining
        abc = wehave + contact - sold_today
        review1 = system - abc
        review2 = abc - remaining

        # Create or update today's stock record
        stock_record, created = Stock.objects.get_or_create(
            store=store,
            date=today,
            defaults={
                'wehave': wehave,
                'contact': contact,
                'sold_today': sold_today,
                'remaining': remaining,
                'system': system,
                'stock_value': stock_value,
                'review1': review1,
                'review2': review2,
            }
        )

        if not created:
            if request.user.is_superuser:
                stock_record.wehave = wehave
                stock_record.contact = contact
                stock_record.sold_today = sold_today
                stock_record.remaining = remaining
                stock_record.system = system
                stock_record.stock_value = stock_value
                stock_record.review1 = review1
                stock_record.review2 = review2
                stock_record.save()
            elif request.user.is_staff:
                stock_record.system = system
                stock_record.stock_value = stock_value
                stock_record.review1 = review1
                stock_record.save()
            else:
                stock_record.contact = contact
                stock_record.sold_today = sold_today
                stock_record.remaining = remaining
                stock_record.review2 = review2
                stock_record.save()

        # ✅ Create Notes with reference to stock_record
        model_names = request.POST.getlist('model_name[]')
        problems = request.POST.getlist('problem[]')

        for model, problem in zip(model_names, problems):
            if model.strip() or problem.strip():
                Note.objects.create(
                    stock=stock_record,        # ✅ Assign the correct stock
                    store=store,
                    user=request.user,
                    model_name=model.strip(),
                    problem=problem.strip()
                )

        return redirect('store_stock_view', store_id=store.id)

    return render(request, 'add_stock.html', {
        'store': store,
        'yesterday_remaining': yesterday_remaining,
        'today': today.isoformat(),
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














# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



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








from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser, login_url='/admin/login/')
def add_staff(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = request.POST.get('is_superuser') == 'on'
            user.save()
            messages.success(request, 'Staff member created successfully!')
            return redirect('add_staff')
    else:
        form = UserCreationForm()

    return render(request, 'add_staff.html', {'form': form})



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib import messages
from django.contrib.auth.models import User

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def all_staff(request):
    staff_users = User.objects.filter(is_staff=True)
    return render(request, 'all_staff.html', {'staff_users': staff_users})

from .forms import StaffEditForm

@login_required
@user_passes_test(is_superuser)
def edit_staff(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = StaffEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, 'Staff updated successfully.')
            return redirect('all_staff')
    else:
        form = StaffEditForm(instance=user)

    return render(request, 'edit_staff.html', {'form': form})


@login_required
@user_passes_test(is_superuser)
def delete_staff(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Staff deleted successfully.')
        return redirect('all_staff')
    return render(request, 'delete_staff_confirm.html', {'user': user})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .models import Store, Stock
from .forms import StockForm

@login_required
def add_or_edit_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # Get date from GET or POST (for editing a particular date)
    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = date.today()

    # Get yesterday's remaining stock for opening calculation
    yesterday = selected_date - timedelta(days=1)
    try:
        yesterday_stock = Stock.objects.get(store=store, date=yesterday)
        yesterday_remaining = yesterday_stock.remaining
    except Stock.DoesNotExist:
        yesterday_remaining = 0

    stock = Stock.objects.filter(store=store, date=selected_date).first()

    if request.method == 'POST':
        # Use form if you have it, else manual parsing:
        # Using manual here for clarity:

        try:
            contact = int(request.POST.get('contact') or 0)
        except ValueError:
            contact = 0
        try:
            sold_today = int(request.POST.get('sold_today') or 0)
        except ValueError:
            sold_today = 0
        try:
            remaining = int(request.POST.get('remaining') or 0)
        except ValueError:
            remaining = 0
        try:
            system = int(request.POST.get('system') or 0)
        except ValueError:
            system = 0

        note = request.POST.get('note', '').strip()

        try:
            stock_value = Decimal(request.POST.get('stock_value') or '0')
        except InvalidOperation:
            stock_value = Decimal('0')

        # Calculation
        wehave = yesterday_remaining
        abc = wehave + contact - sold_today
        review1 = system - abc
        review2 = abc - remaining

        # Save or update the Stock record
        if stock is None:
            stock = Stock(store=store, date=selected_date)
        stock.wehave = wehave
        stock.contact = contact
        stock.sold_today = sold_today
        stock.remaining = remaining
        stock.system = system
        stock.stock_value = stock_value
        stock.review1 = review1
        stock.review2 = review2
        stock.save()

        # Save Notes
        model_names = request.POST.getlist('model_name[]')
        problems = request.POST.getlist('problem[]')

        for model, problem in zip(model_names, problems):
            if model.strip() or problem.strip():
                Note.objects.create(
                    stock=stock,
                    store=store,
                    user=request.user,
                    model_name=model.strip(),
                    problem=problem.strip()
                )

        recalculate_stock_chain(store, selected_date)

        return redirect('store_stock_view', store_id=store.id)

    else:
        # GET request: show form with existing stock data or blank
        context = {
            'store': store,
            'selected_date': selected_date,
            'yesterday_remaining': yesterday_remaining,
            'stock': stock,
        }
        return render(request, 'add_or_edit_stock.html', context)

def recalculate_stock_chain(store, from_date):
    """
    Recalculate opening (wehave), remaining, and reviews for stocks from from_date onwards
    """
    stocks = Stock.objects.filter(store=store, date__gte=from_date).order_by('date')

    # Get previous stock before from_date for opening calculation
    try:
        prev_stock = Stock.objects.filter(store=store, date__lt=from_date).latest('date')
    except Stock.DoesNotExist:
        prev_stock = None

    for stock in stocks:
        # Opening stock (wehave) = previous day's remaining
        if prev_stock:
            stock.wehave = prev_stock.remaining
        else:
            stock.wehave = 0

        # Calculate abc = wehave + contact - sold_today
        abc = stock.wehave + (stock.contact or 0) - (stock.sold_today or 0)

        # review1 = abc - system
        stock.review1 = abc - (stock.system or 0)

        # review2 = abc - remaining
        stock.review2 = abc - (stock.remaining or 0)

        # Calculate remaining if you want to auto-set (optional)
        # stock.remaining = stock.wehave + stock.contact - stock.sold_today

        stock.save()
        prev_stock = stock




from django.shortcuts import render, redirect, get_object_or_404
from .models import Store
from django.contrib.auth.decorators import login_required

@login_required
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        store.name = request.POST['name']
        store.location = request.POST.get('location', '')
        store.save()
        return redirect('register_store')
    return render(request, 'edit_store.html', {'store': store})

@login_required
def delete_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        store.delete()
        return redirect('register_store')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Store

@login_required
def all_stores(request):
    stores = Store.objects.all()
    return render(request, 'all_stores.html', {'stores': stores})

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Note

@staff_member_required
def view_notes(request):
    if request.user.is_staff:
        Note.objects.filter(seen=False).update(seen=True)

    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'view_notes.html', {'notes': notes})


@staff_member_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        note.model_name = request.POST.get('model_name')
        note.problem = request.POST.get('problem')
        note.save()
        return redirect('view_notes')
    return render(request, 'edit_note.html', {'note': note})


@staff_member_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        note.delete()
        return redirect('view_notes')
    return render(request, 'delete_confirm.html', {'note': note})
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def notes_list(request):
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'notes_list.html', {'notes': notes})
