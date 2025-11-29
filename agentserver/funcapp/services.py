from .models import Email, Client
import os
from utils.FileUtil import get_all_files_under_path
from utils.outlook_functions import read_outlook_mail
from qwen_agent.agents import Assistant
from .apps import agent_orchestra
from qwen_agent.utils.output_beautify import typewriter_print
import json5
from utils.GeneralReponseBody import GeneralResponseBody
from django.conf import settings



def prepare_messages_for_chat_over_email(message_id: int, messages_from_request: list):
    '''

    :param message_id:
    :param messages_from_request:
    :param stream:
    :return:
    '''
    # Get the email from DB.
    email = None
    try:
        email: Email = Email.objects.get(message_id=message_id)
    except Email.DoesNotExist:
        return "Target email not found.", 1, []

    if email.status == 'IGNORED':
        return "This email has been ignored.", 1, []
    elif email.status == 'HUMAN':
        return "This email should be replied by a human auditor.", 1, []

    client = None
    try:
        client: Client = Client.objects.get(email_address=email.sender)
    except Client.DoesNotExist:
        return "Corresponding client is not found.", 1, []

    # Prepare the attachments.
    attachment_folder = os.path.join(settings.ACCESSIBLE_ROOT, email.entry_id)
    attachment_paths = get_all_files_under_path(attachment_folder)

    # Prepare the messages.
    messages = []
    messages.append({'role': 'system',
                     'content': settings.PROMPT_TEMPLATE_SYSTEM_CHAT % (client.client_name, message_id)})

    messages.append(
        {'role': 'user', 'content': 'The email subject is "%s", the body is "%s".' % (email.subject, email.body)})

    if len(attachment_paths) > 0:
        for attach_idx, each_path in enumerate(attachment_paths):
            messages.append({'role': 'user',
                             'content': [{'text': 'This is attachment #%d.' % attach_idx}, {'file': each_path}]})
    messages.append({'role': 'user', 'content': 'This is what we know about the client: ' + str(client)})

    messages.extend(messages_from_request)

    return "Messages prepared.", 0, messages


def register_all_emails_service():
    emails = read_outlook_mail(settings.ACCESSIBLE_ROOT)
    all_clients = Client.objects.all()
    existing_emails = Email.objects.all()

    emails_of_unknown_sources = [each_email for each_email in emails if
                                 each_email['Sender'] not in [each_client.email_address for each_client in
                                                              all_clients] and each_email[
                                     'Entry_ID'] not in [each_email.entry_id for each_email in existing_emails]]
    if len(emails_of_unknown_sources) > 0:
        # Write them to DB.
        for each_email in emails_of_unknown_sources:
            ignored_email = Email.objects.create(sender=each_email['Sender'], subject=each_email['Subject'],
                                                 body=each_email['Body'], entry_id=each_email['Entry_ID'],
                                                 status='IGNORED', audit_pass=False)
            ignored_email.save()

    # Filter the emails by sender and entry_id. If the sender doesn't belong to any client or the entry_id already exists, drop off.
    emails = [each_email for each_email in emails if
              each_email['Sender'] in [each_client.email_address for each_client in all_clients] and each_email[
                  'Entry_ID'] not in [each_email.entry_id for each_email in existing_emails]]

    agent: Assistant = agent_orchestra['messanger']

    for each_email in emails:
        messages = [
            {'role': 'user',
             'content': 'This is an email from our customer. '
                        'Please register the following email to DB:\n' + json5.dumps(each_email, indent=4)}
        ]
        response_plain_text = ''
        for each_resp in agent.run(messages=messages):
            response_plain_text = typewriter_print(each_resp, response_plain_text)

    return GeneralResponseBody(message="Registered %d new emails." % len(emails), status=0, data=None)


def prepare_email_audit_messages(message_id: int):
    # Get the email from DB.
    email = None
    try:
        email: Email = Email.objects.get(message_id=message_id)
    except Email.DoesNotExist:
        return "Target email not found.", 1, None

    if email.status == 'IGNORED':
        return "This email has been ignored.", 1, None
    elif email.status == 'HUMAN':
        return "This email should be replied by a human auditor.", 1, []

    client = None
    try:
        client: Client = Client.objects.get(email_address=email.sender)
    except Client.DoesNotExist:
        return "Corresponding client is not found.", 1, None

    # Prepare the attachments.
    attachment_folder = os.path.join(settings.ACCESSIBLE_ROOT, email.entry_id)
    attachment_paths = get_all_files_under_path(attachment_folder)

    # Prepare the messages.
    messages = []
    messages.append({'role': 'system',
                     'content': settings.PROMPT_TEMPLATE_SYSTEM_AUDIT % (client.client_name, message_id)})

    messages.append(
        {'role': 'user', 'content': 'The email subject is "%s", the body is "%s".' % (email.subject, email.body)})
    if len(attachment_paths) > 0:
        for attach_idx, each_path in enumerate(attachment_paths):
            messages.append({'role': 'user',
                             'content': [{'text': 'This is attachment #%d.' % attach_idx}, {'file': each_path}]})
    else:
        messages.append({'role': 'user', 'content': 'The client\'s email didn\'t provide any attachment. '
                                                    'Please judgement this transaction as invalid.'})

    messages.append(
        {'role': 'user', 'content': 'The client\'s total asset value is $%f. '
                                    'The transaction should also follow this regulation: "%s"'
                                    % (client.total_asset_value, client.profile)})

    return "Messages prepared.", 0, messages
