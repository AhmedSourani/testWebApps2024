from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from register.models import Account


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    CURRENCY = (
        ('GBP', 'Pounds'),
        ('USD', 'Dollars'),
        ('EUR', 'Euros')
    )

    currency = forms.ChoiceField(choices=CURRENCY)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, *args, **kwargs):
        instance = super(RegisterForm, self).save(*args, **kwargs)
        Account.objects.create(user=instance, amount=1000, currency=self.cleaned_data["currency"])
        return instance
