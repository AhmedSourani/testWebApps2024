from django.contrib.auth.models import User
from django.db import models

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.amount}"
