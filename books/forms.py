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

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating


class BookForm(forms.ModelForm):
    author_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Book
        exclude = ['author', 'quantity']


class BookFormEdit(forms.ModelForm):
    class Meta:
        model = Book

        exclude = ['title', 'author', 'quantity', 'category']
