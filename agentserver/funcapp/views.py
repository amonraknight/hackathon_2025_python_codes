from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse
from utils.GeneralReponseBody import GeneralResponseBody
from utils.outlook_functions import read_outlook_mail, send_an_email
from utils.constants import *
from .apps import auditor_agent
from qwen_agent.agents import Assistant
import json5
from qwen_agent.utils.output_beautify import typewriter_print
from .models import Email, Client
from django.forms.models import model_to_dict
import os
from utils.FileUtil import get_all_files_under_path


# Create your views here.
def index(request):
    return HttpResponse('Hello world')


@csrf_exempt
def register_all_outlook_emails(request):
    if request.method == 'POST':

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

        response = GeneralResponseBody(message="Registered %d new emails." % len(emails), status=0, data=None)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")


@csrf_exempt
def audit_email_by_message_id(request, message_id):
    '''
    Audit a given email.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':
        # Get the email from DB.
        email = None
        try:
            email: Email = Email.objects.get(message_id=message_id)
        except Email.DoesNotExist:
            response = GeneralResponseBody(message="Target email not found.", status=1, data=None)
            return JsonResponse(response.get_response_body())

        if email.status == 'IGNORED':
            response = GeneralResponseBody(message="This email has been ignored.", status=1, data=None)
            return JsonResponse(response.get_response_body())

        client = None
        try:
            client: Client = Client.objects.get(email_address=email.sender)
        except Client.DoesNotExist:
            response = GeneralResponseBody(message="Corresponding client is not found.", status=1, data=None)
            return JsonResponse(response.get_response_body())

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

        response = GeneralResponseBody(message="Registered all emails.", status=1, data=reply)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")


@csrf_exempt
def acquire_all_emails(request):
    '''
    Acquire all emails from DB which is not in status IGNORED.
    :param request:
    :return:
    '''
    if request.method == 'POST':
        valid_emails = Email.objects.exclude(status="IGNORED").values()
        valid_emails = list(valid_emails)
        response = GeneralResponseBody(message="Registered all emails.", status=0, data=valid_emails)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def acquire_target_email(request, message_id):
    '''
    Acquire a target email from DB which is not in status IGNORED.
    :param message_id:
    :param request:
    :return:
    '''
    if request.method == 'POST':
        try:
            email: Email = Email.objects.get(message_id=message_id)

            response = GeneralResponseBody(message="Email found.", status=0, data=model_to_dict(email))
        except Email.DoesNotExist:
            response = GeneralResponseBody(message="Target email not found.", status=1, data=None)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def reply_email_by_message_id(request, message_id):
    '''
    Reply a given email. Don't need the agent.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':
        response = None
        try:
            email: Email = Email.objects.get(message_id=message_id)
            # Can reply to the audited emails.
            if email.status == 'AUDITED':
                send_an_email(recipients=[email.sender], subject='re: ' + email.subject, body=email.audit_judgement)
                email.status = 'REPLIED'
                email.save()

                email_dict = model_to_dict(email)
                response = GeneralResponseBody(message="Email replied.", status=0, data=email_dict)
            else:
                email_dict = model_to_dict(email)
                response = GeneralResponseBody(message="This email is not in AUDITED status.", status=1,
                                               data=email_dict)

        except Email.DoesNotExist:
            response = GeneralResponseBody(message="Email doesn't exist.", status=1, data=None)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def chat_over_a_given_email(request, message_id):
    '''
    Chat over a given email.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':
        # Get the email from DB.
        email = None
        try:
            email: Email = Email.objects.get(message_id=message_id)
        except Email.DoesNotExist:
            response = GeneralResponseBody(message="Target email not found.", status=1, data=None)
            return JsonResponse(response.get_response_body())

        if email.status == 'IGNORED':
            response = GeneralResponseBody(message="This email has been ignored.", status=1, data=None)
            return JsonResponse(response.get_response_body())

        client = None
        try:
            client: Client = Client.objects.get(email_address=email.sender)
        except Client.DoesNotExist:
            response = GeneralResponseBody(message="Corresponding client is not found.", status=1, data=None)
            return JsonResponse(response.get_response_body())

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


        # Get request body.
        messages_in_request = json5.loads(request.body.decode('utf-8'))

        messages.extend(messages_in_request)

        # Get the agent.
        agent: Assistant = auditor_agent

        reply = []
        response_plain_text = ''
        for reply in agent.run(messages=messages):
            response_plain_text = typewriter_print(reply, response_plain_text)

        response = GeneralResponseBody(message="Chat got replied.", status=0, data=reply)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def reset_test_emails(request):
    '''
    Reset the test emails.
    :param request:
    :return:
    '''
    if request.method == 'GET':
        valid_emails = Email.objects.exclude(status='IGNORED')
        for each in valid_emails:
            each.status = 'NEW'
            each.audit_judgement = ''
            each.audit_pass = False
            each.save()

        response = GeneralResponseBody(message="All emails reset.", status=0, data=None)

        return JsonResponse(response.get_response_body())

    else:
        Http404("Request method should be GET.")
        return None
