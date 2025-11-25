from .models import Email, Client
from utils.constants import ACCESSIBLE_ROOT
import os
from utils.FileUtil import get_all_files_under_path
from utils.outlook_functions import read_outlook_mail
from qwen_agent.agents import Assistant
from .apps import auditor_agent
from qwen_agent.utils.output_beautify import typewriter_print
import json5
from utils.GeneralReponseBody import GeneralResponseBody


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

    client = None
    try:
        client: Client = Client.objects.get(email_address=email.sender)
    except Client.DoesNotExist:
        return "Corresponding client is not found.", 1, []

    # Prepare the attachments.
    attachment_folder = os.path.join(ACCESSIBLE_ROOT, email.entry_id)
    attachment_paths = get_all_files_under_path(attachment_folder)

    # Prepare the messages.
    messages = []
    messages.append({'role': 'system',
                     'content': 'You are going to assist the user to audit a transaction '
                                'by client %s through email (message_id="%d"). '
                                'Answer the user\'s question or follow the users instruction. '
                                'The user is going to provide the details of the email, the attachment, the client.'
                                % (client.client_name, message_id)})

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
    emails = read_outlook_mail(ACCESSIBLE_ROOT)
    all_clients = Client.objects.all()
    existing_emails = Email.objects.all()

    # Filter the emails by sender and entry_id. If the sender doesn't belong to any client or the entry_id already exists, drop off.
    emails = [each_email for each_email in emails if
              each_email['Sender'] in [each_client.email_address for each_client in all_clients] and each_email[
                  'Entry_ID'] not in [each_email.entry_id for each_email in existing_emails]]

    agent: Assistant = auditor_agent

    for each_email in emails:
        messages = [
            {'role': 'user',
             'content': 'Please register the following email to DB:\n' + json5.dumps(each_email, indent=4)}
        ]
        response_plain_text = ''
        for each_resp in agent.run(messages=messages):
            response_plain_text = typewriter_print(each_resp, response_plain_text)

    return GeneralResponseBody(message="Registered %d new emails." % len(emails), status=0, data=None)

def audit_email_service(message_id: int):
    # Get the email from DB.
    email = None
    try:
        email: Email = Email.objects.get(message_id=message_id)
    except Email.DoesNotExist:
        return GeneralResponseBody(message="Target email not found.", status=1, data=None)

    if email.status == 'IGNORED':
        return GeneralResponseBody(message="This email has been ignored.", status=1, data=None)

    client = None
    try:
        client: Client = Client.objects.get(email_address=email.sender)
    except Client.DoesNotExist:
        return GeneralResponseBody(message="Corresponding client is not found.", status=1, data=None)

    # Prepare the attachments.
    attachment_folder = os.path.join(ACCESSIBLE_ROOT, email.entry_id)
    attachment_paths = get_all_files_under_path(attachment_folder)

    # Get the agent.
    agent: Assistant = auditor_agent

    # Prepare the messages.
    messages = []
    messages.append({'role': 'system',
                     'content': 'Please audit a transaction from client %s through email (message_id="%d"). '
                                'The user will provide the email content, attached transaction detail files'
                                ' and the client\'s profile as reference. '
                                'If you consider the transaction valid, please set audit_pass as true and congratulate the client. '
                                'Otherwise, please set audit_pass as false and tell the client the reason.'
                                'Use tool "add_audit_judgement" to add your judgement to DB.'
                                % (client.client_name, message_id)})

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
        {'role': 'user', 'content': 'The transaction should also follow this regulation: "%s"' % client.profile})

    reply = []
    response_plain_text = ''
    for reply in agent.run(messages=messages):
        response_plain_text = typewriter_print(reply, response_plain_text)

    return GeneralResponseBody(message="Registered all emails.", status=1, data=reply)