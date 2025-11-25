from django.apps import AppConfig
from agent.bot import get_a_customized_agent
from dotenv import load_dotenv
from utils.constants import *
from qwen_agent.tools.base import BaseTool, register_tool
import json5
from utils.outlook_functions import send_an_email

auditor_agent = None

# Write all the functions here so they will be loaded to .
@register_tool('send_email')
class SendEmail(BaseTool):
    description = 'Send out an email to given recipients.'
    parameters = [
        {
            'name': 'recipients',
            'description': 'A list of email addresses as the recipients of the email, separated by ";".',
            'type': 'string',
            'required': True
        },
        {
            'name': 'subject',
            'description': 'The subject of the email.',
            'type': 'string',
            'required': True
        },
        {
            'name': 'body',
            'description': 'The email body.',
            'type': 'string',
            'required': True
        }
    ]

    def call(self, params: str, **kwargs) -> str:
        recipients = json5.loads(params)['recipients']
        subject = json5.loads(params)['subject']
        body = json5.loads(params)['body']

        # Split recipients by ";".
        recipients_list = recipients.split(';')

        send_an_email(recipients_list, subject, body)

        return 'Email sent.'


class FuncappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcapp'

    def ready(self):
        global auditor_agent
        if auditor_agent is None:
            load_dotenv()
            tools = [
                {'mcpServers': {  # You can specify the MCP configuration file
                    "filesystem": {
                        "command": "npx",
                        "args": [
                            "-y",
                            "@modelcontextprotocol/server-filesystem",
                            ACCESSIBLE_ROOT
                        ]
                    },
                    "playwright": {
                        "command": "npx",
                        "args": [
                            "@playwright/mcp@latest"
                        ]
                    }
                }
                },
                'get_target_message',
                'register_a_message',
                'add_audit_judgement',
                'send_email'
            ]
            system_message = '''
            You are an AI auditor of stock transactions. 
            Make judgements according to clients' documents, market rules and client profile.
            1. Use Playwright to search for stock information on the web.
            2. Use Filesystem to read the clients' documents.
            3. Regulations will be provided as a context.
            4. Make your decisions and write your judgement.
            5. Reply the human auditor's doubts in chat.
            '''
            auditor_agent = get_a_customized_agent(tools=tools, system_message=system_message)
