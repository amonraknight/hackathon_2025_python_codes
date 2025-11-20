from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse
from utils.GeneralReponseBody import GeneralResponseBody
from utils.outlook_functions import read_outlook_mail
from utils.constants import *
from .apps import auditor_agent
from qwen_agent.agents import Assistant
import json5
from qwen_agent.utils.output_beautify import typewriter_print


# Create your views here.
def index(request):
    return HttpResponse('Hello world')


@csrf_exempt
def register_all_outlook_emails(request):
    if request.method == 'POST':

        emails = read_outlook_mail(ACCESSIBLE_ROOT)
        agent: Assistant = auditor_agent

        for each_email in emails:
            messages = [
                {'role': 'user',
                 'content': 'Please register the following email to DB:\n' + json5.dumps(each_email, indent=4)}
            ]
            response_plain_text = ''
            for each_resp in agent.run(messages=messages):
                response_plain_text = typewriter_print(each_resp, response_plain_text)
                print(response_plain_text)

        response = GeneralResponseBody(message="Registered all emails.", status=1, data=None)

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
def reply_email_by_message_id(request, message_id):
    '''
    Reply a given email.
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
