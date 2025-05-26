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
