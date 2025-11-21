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

        response = GeneralResponseBody(message="Registered all emails.", status=0, data=None)

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
        response = GeneralResponseBody(message="Registered all emails.", status=1, data=None)

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
        Http404("Request method should be GET.")


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
                response = GeneralResponseBody(message="This email is not in AUDITED status.", status=1, data=email_dict)

        except Email.DoesNotExist:
            response = GeneralResponseBody(message="Email doesn't exist.", status=1, data=None)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")


@csrf_exempt
def chat_over_a_given_email(request, message_id):
    '''
    Chat over a given email.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':
        response = GeneralResponseBody(message="Registered all emails.", status=1, data=None)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
