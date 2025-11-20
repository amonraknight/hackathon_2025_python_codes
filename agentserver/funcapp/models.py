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


@register_tool('register_an_email')
class RegisterAnEmail(BaseTool):
    description = 'Register an email by inserting entry_id, subject, sender, body to DB with a status.'
    parameters = [
        {
            'name': 'entry_id',
            'description': 'The entry ID of an email.',
            'type': 'string',
            'required': True
        },
        {
            'name': 'subject',
            'description': 'The subject of an email.',
            'type': 'string',
            'required': True
        },
        {
            'name': 'sender',
            'description': 'The sender of an email.',
            'type': 'string',
            'required': True
        },
        {
            'name': 'body',
            'description': 'The body of an email.',
            'type': 'string',
            'required': True
        },
        {
            'name': 'status',
            'description': 'If the email is about financial transaction, write "NEW". Otherwise write "IGNORED".',
            'type': 'string',
            'required': True
        }
    ]

    def call(self, params: str, **kwargs) -> str:
        entry_id = json5.loads(params)['entry_id']
        subject = json5.loads(params)['subject']
        sender = json5.loads(params)['sender']
        body = json5.loads(params)['body']
        status = json5.loads(params)['status']

        if Email.objects.filter(entry_id=entry_id).exists():
            return 'This email has previously been registered. Message Id %d.' % Email.objects.get(
                entry_id=entry_id).message_id
        else:
            email = Email(entry_id=entry_id, subject=subject, sender=sender, body=body, status=status, audit_pass=False,
                          audit_judgement="")
            email.save()
        return 'This email has been registered. Message Id %d.' % email.message_id
