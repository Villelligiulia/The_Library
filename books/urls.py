from django.urls import path
from . import views


urlpatterns = [

    path('', views.book_list, name='book_list'),
    path('search-book/', views.search_book, name='search_book'),
]
