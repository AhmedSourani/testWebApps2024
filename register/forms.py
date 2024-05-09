from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from register.models import Account


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    CURRENCY = (
        ('GBP', 'Pounds £'),
        ('USD', 'Dollars $'),
        ('EUR', 'Euros € ')
    )

    currency = forms.ChoiceField(choices=CURRENCY)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "currency")

    # def save(self, *args, **kwargs):
    #     instance = super(RegisterForm, self).save(*args, **kwargs)
    #     Account.objects.create(user=instance, amount=1000, currency=self.cleaned_data["currency"])
    #     return instance
    def save(self, *args, **kwargs):
        instance = super(RegisterForm, self).save(*args, **kwargs)
        try:
            Account.objects.create(user=instance, amount=1000, currency=self.cleaned_data["currency"])
        except Exception as e:
            # Handle the exception, maybe log it or modify the method to handle it externally
            print(f"Failed to create account: {str(e)}")
            # Optionally, you could handle the error more gracefully depending on your application needs
        return instance




from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AdminRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(required=True, help_text='Required.')  # Add this if not automatically included

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']  # Make sure to save the email to the user object
        if commit:
            user.save()
        return user



