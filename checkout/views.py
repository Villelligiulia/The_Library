import os
import stripe
from django.views.decorators.http import require_POST

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse, HttpResponse
from checkout.forms import CheckoutForm
from checkout.models import Order, OrderLineItem
from decimal import Decimal
from books.models import Book
from django.conf import settings
from django.http import HttpResponse
from cart.context import cart_content

import json


# def checkout(request):
#     stripe_public_key = settings.STRIPE_PUBLIC_KEY
#     stripe_secret_key = settings.STRIPE_SECRET_KEY

#     # Check if the cart is empty
#     cart = request.session.get('cart', {})
#     if not cart:
#         messages.error(
#             request, 'At the moment our cart is empty. Please add items to your cart.')
#         return redirect('book_list')

#     current_cart = cart_content(request)
#     total = current_cart['total_price']
#     stripe_total = round(total * 100)
#     stripe.api_key = stripe_secret_key
#     intent = stripe.PaymentIntent.create(
#         amount=stripe_total,
#         currency=settings.STRIPE_CURRENCY,
#     )
#     print(intent, 'sora lellaaaa')

#     # Retrieve cart items and total price
#     items = []
#     total_price = Decimal(0)
#     for item in cart.values():
#         item['price'] = Decimal(item['price'])
#         total_price += item['price'] * item['quantity']
#         book = get_object_or_404(Book, id=item['book_id'])
#         items.append({
#             'book': book,
#             'quantity': item['quantity'],
#             'subtotal': item['price'] * item['quantity'],
#         })

#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)

#         if form.is_valid():
#             save_to_profile = form.cleaned_data['save_to_profile']

#         if save_to_profile:

#             request.session['checkout_info'] = form.cleaned_data

#         else:
#             request.session['checkout_info'] = None

#             order = Order(
#                 user=request.user,
#                 first_name=form.cleaned_data['first_name'],
#                 last_name=form.cleaned_data['last_name'],
#                 email=form.cleaned_data['email'],
#                 address=form.cleaned_data['address'],
#                 city=form.cleaned_data['city'],
#                 state=form.cleaned_data['state'],
#                 country=form.cleaned_data['country'],
#                 postal_code=form.cleaned_data['postal_code'],
#                 save_to_profile=save_to_profile,


#             )

#         order.save()
#         for item in items:
#             book = item['book']
#             quantity = item['quantity']
#             OrderLineItem.objects.create(
#                 order=order, book=book, quantity=quantity)

#         # Clear the cart
#         request.session['cart'] = {}

#     # Redirect the user to the to checkout_success after successful checkout
#         return redirect(reverse('checkout_success', args=[order.order_number]))

#     else:

#         initial_data = {

#         }

#         form = CheckoutForm(initial_data=initial_data)

#         context = {
#             'form': form,
#             'cart_items': items,
#             'stripe_public_key': stripe_public_key,
#             'client_secret': intent.client_secret,


#         }
#         return render(request, 'checkout/checkout.html', context)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Retrieve cart items and total price
    items = []

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        form = CheckoutForm(request.POST)

        if form.is_valid():
            save_to_profile = form.cleaned_data.get('save_to_profile', False)

            order = Order(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=form.cleaned_data['country'],
                postal_code=form.cleaned_data['postal_code'],
                save_to_profile=save_to_profile,
                # Save the checkout form
                checkout_first_name=form.cleaned_data['first_name'],
                checkout_last_name=form.cleaned_data['last_name'],
                checkout_email=form.cleaned_data['email'],
                checkout_address=form.cleaned_data['address'],
                checkout_city=form.cleaned_data['city'],
                checkout_state=form.cleaned_data['state'],
                checkout_country=form.cleaned_data['country'],
                checkout_postal_code=form.cleaned_data['postal_code'],
                checkout_save_to_profile=save_to_profile,
            )

            order.save()

            for item in cart.values():
                book = get_object_or_404(Book, id=item['book_id'])
                OrderLineItem.objects.create(
                    order=order, book=book, quantity=item['quantity'])

            # Clear the cart
            request.session['cart'] = {}

            # Redirect the user to the checkout_success page after successful checkout
            return redirect(reverse('checkout_success', args=[order.order_number]))

    else:
        # Check if the cart is empty
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(
                request, 'At the moment our cart is empty. Please add items to your cart.')
            return redirect('book_list')

        current_cart = cart_content(request)
        total = current_cart['total_price']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        print(intent, 'sora lellaaaa')

        initial_data = {}
        saved_checkout_info = request.session.get('checkout_info', {})
        if saved_checkout_info:
            initial_data.update(saved_checkout_info)

        # Initialize the form for the GET request
        form = CheckoutForm(initial=initial_data)

        context = {
            'form': form,
            'cart_items': items,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Order successfully processed! \
        Thank you for shopping with us !!')

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'save_to_profile': order.save_to_profile,
    }

    return render(request, template, context)
