from django.urls import path
from profiles.views import profile, edit_profile

urlpatterns = [

    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),

]
