from django.db import models

# Create your models here.
class Email(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    entry_id = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    sender = models.EmailField(max_length=254)
    body = models.TextField()
    status = models.CharField(max_length=10)
    audit_pass = models.BooleanField()
    audit_judgement = models.TextField()

class Client(models.Model):
    client_id = models.BigAutoField(primary_key=True)
    client_name = models.CharField(max_length=50)
    email_address = models.EmailField(max_length=254)
    profile = models.TextField()