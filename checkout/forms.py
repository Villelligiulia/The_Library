from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email',
                  'address',
                  'city', 'postal_code', 'country',
                  'state', 'save_to_profile')

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.pop('initial_data', None)
        super().__init__(*args, **kwargs)
        if initial_data:
            self.initial = initial_data

    def clean_email(self):
        email = self.cleaned_data['email']
        return email
