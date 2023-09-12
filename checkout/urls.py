from django.urls import path
from checkout.views import checkout, checkout_success, stripe_webhook

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('checkout_success/<order_number>',
         checkout_success, name='checkout_success'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),

]
