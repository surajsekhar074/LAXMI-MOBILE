from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class StaffRegistrationForm(UserCreationForm):
    is_superuser = forms.BooleanField(
        required=False,
        label='Grant Superuser Privileges',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),

        }


from django import forms
from django.contrib.auth.models import User

class StaffEditForm(forms.ModelForm):
    password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

from django import forms
from .models import Stock

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['date', 'wehave', 'contact', 'sold_today', 'remaining', 'system', 'stock_value', 'review1', 'review2',]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

## views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Store, Stock

from django.contrib.auth.decorators import login_required
from datetime import date
from django import forms
from .models import Stock  # ✅ Correct


@login_required
def add_or_edit_stock(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    # Get the selected date from query params or use today
    selected_date = request.GET.get('date') or date.today().isoformat()

    # Get or create stock entry for that date
    stock, created = Stock.objects.get_or_create(
        store=store,
        date=selected_date,
        defaults={'created_by': request.user}
    )

    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save(commit=False)

            # Optional calculation: update physical_difference if it exists
            if hasattr(stock, 'system') and hasattr(stock, 'remaining'):
                stock.physical_difference = stock.remaining - stock.system

            stock.created_by = request.user
            stock.save()
            return redirect('store_stock_view', store_id=store.id)
    else:
        form = StockForm(instance=stock)

    return render(request, 'add_or_edit_stock.html', {
        'form': form,
        'store': store,
        'selected_date': selected_date,
        'is_edit': not created,
    })

