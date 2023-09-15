import uuid
from django.db.models import Sum
from django.db import models
from django.conf import settings
from books.models import Book
from django_countries.fields import CountryField


class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    address = models.CharField(max_length=200, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=100, null=False, blank=False)
    country = CountryField(blank_label='Country *',
                           max_length=100, null=False, blank=True)
    postal_code = models.CharField(max_length=20, null=False, blank=True)
    order_number = models.CharField(max_length=32, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, default=0)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    save_to_profile = models.BooleanField(default=False)
    # New fields to store checkout form data
    checkout_first_name = models.CharField(
        max_length=100, blank=True, null=True)
    checkout_last_name = models.CharField(
        max_length=100, blank=True, null=True)
    checkout_email = models.EmailField(blank=True, null=True)

    checkout_address = models.CharField(max_length=200, blank=True, null=True)
    checkout_city = models.CharField(max_length=100, blank=True, null=True)
    checkout_state = models.CharField(max_length=100, blank=True, null=True)
    checkout_country = models.CharField(max_length=100, blank=True, null=True)
    checkout_postal_code = models.CharField(
        max_length=20, blank=True, null=True)
    checkout_save_to_profile = models.BooleanField(default=False)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        ADD or 0 in the next line when doing the signal
        """
        lineitem_total = self.lineitems.aggregate(models.Sum('lineitem_total'))
        [
            'lineitem_total__sum'] or 0
        if lineitem_total is not None:
            self.order_total = lineitem_total
            if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
                self.delivery_cost = self.order_total * \
                    settings.STANDARD_DELIVERY_PERCENTAGE / 100
            else:
                self.delivery_cost = 0
            self.grand_total = self.order_total + self.delivery_cost
            self.save()

    def __str__(self):
        return f"Order #{self.pk} - {self.first_name} {self.last_name}"


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='lineitems')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total,
        update the order total, and save the associated order.
        """
        self.lineitem_total = self.book.price * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total()

    def __str__(self):
        return f"OrderLineItem: {self.book.title} - Quantity: {self.quantity}"
