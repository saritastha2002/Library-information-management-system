from django.urls import path,include
from .views import *
from . import views


urlpatterns = [
    
    path('home/',views.home,name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.member_dashboard, name='member_dashboard'),
    
    path('readers/', views.readers_tab, name='readers_tab'),
    path('readers/add/',views.save_reader,name="save_reader"),
    path("readers/update/<int:id>/", views.update_reader, name="update_reader"),
    path("readers/delete/<int:id>/", views.delete_reader, name="delete_reader"),
    path('books/add/', views.add_book, name='add_book'),
    path('books/', views.book_list, name='book_list'),
    path('books/update/<int:book_id>/', views.update_book, name='update_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('books/increase/<int:book_id>/', views.increase_quantity, name='increase_quantity'),
    path('books/decrease/<int:book_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('records/', views.records_tab, name='records_tab'),
    path('records/add/', views.add_borrowing, name='add_borrowing'),
    path('returns/', views.returns_tab, name='returns_tab'),
    path('returns/<int:borrowing_id>/', views.return_book, name='return_book'),
]
