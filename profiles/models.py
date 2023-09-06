from django.db import models
from django.contrib.auth.models import User
from checkout.models import Order  


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    order_history = models.ManyToManyField(Order, blank=True)

    def __str__(self):
        return self.user.username
