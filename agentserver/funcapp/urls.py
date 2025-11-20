from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register_all", views.register_all_outlook_emails, name="register_all_outlook_emails"),
    path("audit_email/<int:message_id>", views.audit_email_by_message_id, name="audit_email_by_message_id"),
    path("reply_email/<int:message_id>", views.reply_email_by_message_id, name="reply_email_by_message_id"),
    path("chat/<int:message_id>", views.chat_over_a_given_email, name="chat_over_a_given_email")
]