from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register_all_outlook_emails", views.register_all_outlook_emails, name="register_all_outlook_emails"),
]