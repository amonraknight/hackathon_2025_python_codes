from .models import Email, Client
from utils.constants import ACCESSIBLE_ROOT
import os
from utils.FileUtil import get_all_files_under_path



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


