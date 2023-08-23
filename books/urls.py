from django.urls import path
from . import views


urlpatterns = [

    path('', views.book_list, name='book_list'),
    path('search-book/', views.search_book, name='search_book'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('all_categories/', views.all_categories, name='all_categories'),
    path('best-sellers/', views.best_sellers, name='best_sellers'),
]
