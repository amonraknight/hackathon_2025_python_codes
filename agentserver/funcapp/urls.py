from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register_all", views.register_all_outlook_emails, name="register_all_outlook_emails"),
    path("acquire_all", views.acquire_all_emails, name="acquire_all_emails"),
    path("audit_email/<int:message_id>", views.audit_email_by_message_id, name="audit_email_by_message_id"),
    path("reply_email/<int:message_id>", views.reply_email_by_message_id, name="reply_email_by_message_id"),
    path("chat/<int:message_id>", views.chat_over_a_given_email, name="chat_over_a_given_email"),
    path("reset", views.reset_test_emails, name="reset_test_emails"),
    path("acquire_target_email/<int:message_id>", views.acquire_target_email, name="acquire_target_email"),
    path("chat_stream/<int:message_id>", views.chat_over_a_given_email_stream, name="chat_over_a_given_email_stream"),
    path("test_streaming", views.test_streaming_response, name="test_streaming_response")
]