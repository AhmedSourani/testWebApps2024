from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # Importing the default User model

class Transaction(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_transactions"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_transactions"
    )
    sent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00  # Set a sensible default
    )
    received_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00  # Set a sensible default
    )
    sent_currency = models.CharField(
        max_length=3,
        choices=(
            ('GBP', 'Pounds £'),
            ('USD', 'Dollars $'),
            ('EUR', 'Euros €'),
        ),
        default='GBP'
    )
    received_currency = models.CharField(
        max_length=3,
        choices=(
            ('GBP', 'Pounds £'),
            ('USD', 'Dollars $'),
            ('EUR', 'Euros €'),
        ),
        default='GBP'
    )
    date = models.DateTimeField(auto_now_add=True)
    def transaction_summary(self):
        return f"{self.sent_amount} {self.sent_currency} sent, {self.received_amount} {self.received_currency} received"
    def __str__(self):
        return f"{self.sent_amount} {self.sent_currency} from {self.sender} to {self.receiver} received as {self.received_amount} {self.received_currency}"

class Request(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester")
    giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="giver")
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    pending = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')  # For example, 'GBP', 'USD', 'EUR'