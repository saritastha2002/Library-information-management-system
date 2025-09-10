from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('home/', home),
    path('readers/', views.readers_tab, name='readers_tab'),
    path('readers/add/',views.save_reader,name="save_reader"),
    path("readers/update/<int:id>/", views.update_reader, name="update_reader"),
    path("readers/delete/<int:id>/", views.delete_reader, name="delete_reader"),
   
]
