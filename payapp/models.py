from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    date = models.DateTimeField(auto_now_add=True)


class Request(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester")
    giver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="giver")
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    pending = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
