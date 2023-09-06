from django.shortcuts import render
from checkout.views import checkout
from checkout.models import Order

# Create your views here.


def profile(request):

    user = request.user
    order = Order.objects.filter(user=user).latest('created_at')
    # True or False based on the save_to_profile value
    show_profile_info = order.save_to_profile
    context = {'user': user, 'order': order,
               'show_profile_info': show_profile_info}
    return render(request, 'profiles/profile.html', context)
