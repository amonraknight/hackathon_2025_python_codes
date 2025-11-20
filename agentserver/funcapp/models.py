from django.db import models
from utils.constants import *
import os
from qwen_agent.tools.base import BaseTool, register_tool
import json5


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

    def __str__(self):
        return ("Here is an email from %s:\n Subject: %s \n "
                "Mail body: %s\n The attachments(if any) are under path \"%s\".") % (
            self.sender, self.subject, self.body, os.path.join(ACCESSIBLE_ROOT, self.entry_id))


class Client(models.Model):
    client_id = models.BigAutoField(primary_key=True)
    client_name = models.CharField(max_length=50)
    email_address = models.EmailField(max_length=254)
    profile = models.TextField()
    total_asset_value = models.FloatField(default=0.0)

    def __str__(self):
        return "Client Name: %s, Client Email Address: %s, Profile: %s, Total Asset Value: %f" % (self.client_name,
                                                                                                  self.email_address,
                                                                                                  self.profile,
                                                                                                  self.total_asset_value)


@register_tool('get_target_email')
class GetTargetEmail(BaseTool):
    description = ('Get the target email by message_id. Returns the sender, subject, body of the email '
                   'and where to find the attachments.')
    parameters = [{
        'name': 'message_id',
        'description': 'The message id of the target email.',
        'type': 'string',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        message_id = int(json5.loads(params)['message_id'])
        try:
            target_email: Email = Email.objects.get(message_id=message_id)
            return str(target_email)
        except Email.DoesNotExist:
            return "Failed to get the target email. Please verify the message_id."