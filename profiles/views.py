from django.shortcuts import render, redirect
from checkout.views import checkout
from checkout.models import Order
from checkout.forms import CheckoutForm
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def profile(request):
    """
    Display user profile, optionally display saved info by the user
    during the checkout process
    """

    user = request.user
    order = Order.objects.filter(user=user).latest('created_at')
    order_history = user.userprofile.order_history.all()
    # True or False based on the save_to_profile value
    show_profile_info = order.save_to_profile
    context = {'user': user, 'order': order,
               'order_history': order_history,
               'show_profile_info': show_profile_info}
    return render(request, 'profiles/profile.html', context)


@login_required
def edit_profile(request):
    """
    Handle edit profile logic :allow user to edit info previously saved
    during the checkout process
    """
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            save_to_profile = form.cleaned_data['save_to_profile']

            if save_to_profile:
                request.session['checkout_info'] = form.cleaned_data

            else:
                request.session['checkout_info'] = None
                # Save the checkout form data to the profile
                user = request.user
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']

                user.address = form.cleaned_data['address']
                user.city = form.cleaned_data['city']
                user.state = form.cleaned_data['state']
                user.country = form.cleaned_data['country']
                user.postal_code = form.cleaned_data['postal_code']
                user.save()

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
                # Save the checkout form data
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

            return redirect('profile')
    form = CheckoutForm()
    return render(request, 'profiles/edit_profile.html', {'form': form})
