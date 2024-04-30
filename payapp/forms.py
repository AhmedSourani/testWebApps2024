from django import forms
from django.contrib.auth.models import User


class SendMoneyForm(forms.Form):
    receiver = forms.ModelChoiceField(User.objects.all())
    amount = forms.DecimalField(label='Amount', decimal_places=2)


class RequestMoneyForm(forms.Form):
    giver = forms.ModelChoiceField(User.objects.all())
    amount = forms.DecimalField(label='Amount', decimal_places=2)
