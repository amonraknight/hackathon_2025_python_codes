from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse
from utils.GeneralReponseBody import GeneralResponseBody

# Create your views here.
def index(request):
    return HttpResponse('Hello world')

@csrf_exempt
def register_all_outlook_emails(request):
    if request.method == 'POST':
        response = GeneralResponseBody(message="Registered all emails.", status=1, data=None)

        return JsonResponse(response.get_response_body())
    else:
        Http404("Request method should be POST.")