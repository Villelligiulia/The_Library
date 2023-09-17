import os
import stripe
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404, reverse
from checkout.forms import CheckoutForm
from checkout.models import Order, OrderLineItem
from decimal import Decimal
from books.models import Book
from django.conf import settings
from django.http import HttpResponse
from cart.context import cart_content
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def stripe_webhook(request):

    if request.method == "POST":
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        if event.type == "charge.succeeded":

            print("Charge succeeded:", event.data.object)

        return HttpResponse(status=200)


def checkout(request):
    """
    Handle the checkout process.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    items = []

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        form = CheckoutForm(request.POST)

        if form.is_valid():
            save_to_profile = form.cleaned_data.get('save_to_profile', False)

            if save_to_profile:

                request.session['checkout_info'] = form.cleaned_data

            else:
                request.session['checkout_info'] = None

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

            request.user.userprofile.order_history.add(order)

            for item in cart.values():
                book = get_object_or_404(Book, id=item['book_id'])
                OrderLineItem.objects.create(
                    order=order, book=book, quantity=item['quantity'])

            request.session['cart'] = {}

            _send_confirmation_email(order)

            return redirect(reverse('checkout_success',
                            args=[order.order_number]))

    else:
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(
                request, 'At the moment our cart is empty. Please add items\
                to your cart.')
            return redirect('book_list')

        current_cart = cart_content(request)
        total = current_cart['total_price']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        print(intent)

        initial_data = {}
        saved_checkout_info = request.session.get('checkout_info', {})
        if saved_checkout_info:
            initial_data.update(saved_checkout_info)

        form = CheckoutForm(initial=initial_data)

        for item in cart.values():
            book = get_object_or_404(Book, id=item['book_id'])
            items.append({
                'book': book,
                'quantity': item['quantity'],
            })

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

    _send_confirmation_email(order)

    if 'cart' in request.session:
        del request.session['cart']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'save_to_profile': order.save_to_profile,
    }

    return render(request, template, context)


logger = logging.getLogger(__name__)


def _send_confirmation_email(order):
    """Send the user a confirmation email"""
    cust_email = order.email
    subject = render_to_string(
        'checkout/confirmation_emails/confirmation_email_subject.txt',
        {'order': order})
    body = render_to_string(
        'checkout/confirmation_emails/confirmation_email_body.txt',
        {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )
        logger.info(f"Confirmation email sent to {cust_email}")
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")
