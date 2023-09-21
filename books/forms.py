from django import forms
from .models import Review, Book
from django.core.exceptions import ValidationError


class ReviewForm(forms.ModelForm):
    class Meta:

        model = Review
        fields = ['comment']
        widgets = {

            'comment': forms.Textarea(attrs={'rows': 5}),

        }


class BookForm(forms.ModelForm):
    author_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Book
        exclude = ['author', 'quantity']


class BookFormEdit(forms.ModelForm):
    class Meta:
        model = Book

        exclude = ['title', 'author', 'quantity', 'category']
