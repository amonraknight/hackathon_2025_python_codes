from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse, StreamingHttpResponse
from utils.GeneralReponseBody import GeneralResponseBody
from utils.QueueDict import QueueDict
from utils.outlook_functions import send_an_email
from .apps import agent_orchestra, chat_history
from qwen_agent.agents import Assistant
import json5
from qwen_agent.utils.output_beautify import typewriter_print
from .models import Email, Client
from django.forms.models import model_to_dict
from utils.GeneralFunctions import iterate_generator
from .services import prepare_messages_for_chat_over_email, register_all_emails_service, prepare_email_audit_messages


# Create your views here.
def index(request):
    return HttpResponse('Hello world')


@csrf_exempt
def register_all_outlook_emails(request):
    if request.method == 'POST':

        response = register_all_emails_service()
        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def audit_email_by_message_id(request, message_id):
    '''
    Audit a given email.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':
        sys_msg_text, status, messages = prepare_email_audit_messages(message_id)
        if status == 1:
            response = GeneralResponseBody(message=sys_msg_text, status=1, data=None)
        else:
            agent: Assistant = agent_orchestra['auditor']
            reply = []
            response_plain_text = ''
            for reply in agent.run(messages=messages):
                response_plain_text = typewriter_print(reply, response_plain_text)

            response = GeneralResponseBody(message="Registered all emails.", status=1, data=reply)
        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def audit_email_by_message_id_stream(request, message_id):
    '''
    Audit a given email. Respond in stream.
    :param request:
    :param message_id:
    :return:
    '''
    sys_msg_text, status, messages = prepare_email_audit_messages(message_id)
    if status == 1:
        response = GeneralResponseBody(message=sys_msg_text, status=1, data=None)
        return JsonResponse(response.get_response_body())
    else:
        agent: Assistant = agent_orchestra['auditor']

        return StreamingHttpResponse(streaming_content=iterate_generator(agent.run(messages=messages)),
                                     content_type='text/plain')


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
            sender = email.sender
            client: Client = Client.objects.get(email_address=sender)

            email_dict = model_to_dict(email)
            client_dict = model_to_dict(client)
            # merge the 2 dicts.
            email_dict.update(client_dict)

            email_dict['created_at'] = email.created_at
            email_dict['updated_at'] = email.updated_at

            response = GeneralResponseBody(message="Email found.", status=0, data=email_dict)
        except Email.DoesNotExist:
            response = GeneralResponseBody(message="Target email not found.", status=1, data=None)
        except Client.DoesNotExist:
            response = GeneralResponseBody(message="Client not found.", status=1, data=None)

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
    Chat over a given email. No streaming.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':

        messages_from_request = json5.loads(request.body.decode('utf-8'))

        last_message = messages_from_request[-1]
        history: QueueDict = chat_history
        history.enqueue(message_id, last_message)
        messages_from_hist = history.get_queue(message_id)

        error_message, status, messages = prepare_messages_for_chat_over_email(message_id, messages_from_hist)
        if status == 1:
            response = GeneralResponseBody(message=error_message, status=1, data=None)
            return JsonResponse(response.get_response_body())
        else:
            agent: Assistant = agent_orchestra['assistant_chat']
            reply = []
            response_plain_text = ''
            for reply in agent.run(messages=messages):
                response_plain_text = typewriter_print(reply, response_plain_text)

            response = GeneralResponseBody(message="Chat got replied.", status=0, data=reply)
            history.enqueue(message_id, reply[-1])

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


@csrf_exempt
def chat_over_a_given_email_stream(request, message_id):
    '''
    Chat over a given email. The output is a steam.
    :param request:
    :param message_id:
    :return:
    '''
    if request.method == 'POST':
        messages_from_request = json5.loads(request.body.decode('utf-8'))

        last_message = messages_from_request[-1]
        history: QueueDict = chat_history
        history.enqueue(message_id, last_message)
        messages_from_his = history.get_queue(message_id)

        error_message, status, messages = prepare_messages_for_chat_over_email(message_id, messages_from_his)
        if status == 1:
            response = GeneralResponseBody(message=error_message, status=1, data=None)
            return JsonResponse(response.get_response_body())
        else:
            agent: Assistant = agent_orchestra['assistant_chat']

            return StreamingHttpResponse(
                streaming_content=iterate_generator(agent.run(messages=messages), history, message_id),
                content_type='text/plain')

    else:
        Http404("Request method should be POST.")
        return None


@csrf_exempt
def get_statistics(request):
    '''
    Get the statistics of the emails. Count the number of emails having status in "NEW", "AUDITED", "REPLIED", "IGNORED".
    Also cauculate the percentage of emails in these statuses.
    :param request:
    :return: JsonResponse
    '''
    if request.method == 'POST':
        new_count = Email.objects.filter(status='NEW').count()
        audited_count = Email.objects.filter(status='AUDITED').count()
        replied_count = Email.objects.filter(status='REPLIED').count()
        ignored_count = Email.objects.filter(status='IGNORED').count()
        human_count = Email.objects.filter(status='HUMAN').count()
        total_count = new_count + audited_count + replied_count + ignored_count + human_count

        statistics = {
            'new_count': new_count,
            'audited_count': audited_count,
            'replied_count': replied_count,
            'ignored_count': ignored_count,
            'total_count': total_count,
            'human_count': human_count,
            'new_percentage': round(new_count / total_count * 100, 2),
            'audited_percentage': round(audited_count / total_count * 100, 2),
            'replied_percentage': round(replied_count / total_count * 100, 2),
            'ignored_percentage': round(ignored_count / total_count * 100, 2),
            'human_percentage': round(human_count / total_count * 100, 2)
        }

        response = GeneralResponseBody(message='Statistics acquired.', status=1, data=statistics)
        return JsonResponse(response.get_response_body())

    else:
        Http404("Request method should be POST.")
        return None
