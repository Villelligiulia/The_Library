from django.urls import path
from . import views


urlpatterns = [

    path('', views.book_list, name='book_list'),
    path('search-book/', views.search_book, name='search_book'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('all_categories/', views.all_categories, name='all_categories'),
    path('best-sellers/', views.best_sellers, name='best_sellers'),
    path('library_management/', views.library_management,
         name='library_management'),
    path('library_management/create/', views.create_book, name='create_book'),
    path('library_management/edit/<int:book_id>/',
         views.edit_book, name='edit_book'),
    path('admin_search-book/', views.admin_search_book, name='admin_search_book'),
]
