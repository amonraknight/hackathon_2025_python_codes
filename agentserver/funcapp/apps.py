from django.apps import AppConfig
from agent.bot import get_a_customized_agent
from utils.QueueDict import QueueDict
from utils.constants import *
from qwen_agent.tools.base import BaseTool, register_tool
import json5
from utils.outlook_functions import send_an_email

agent_orchestra = {}
chat_history = None


def _initiate_agent_orchestra():
    global agent_orchestra
    # If agent_orchestra is empty, start to create agents.
    if len(agent_orchestra) == 0:
        # Create agent messanger.
        agent_orchestra['messanger'] = get_a_customized_agent(tools=['register_a_message'],
                                                              system_message='You are a messanger agent who reads emails and register them to DB.',
                                                              model='qwen-max')
        # Create agent auditor.
        auditor_tools = [
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
            'add_audit_judgement'
        ]
        auditor_system_message = '''
                    You are an AI auditor of stock transactions. 
                    Make judgements according to clients' documents, market rules and client profile.
                    1. Use Playwright to search for stock information from Google finance(https://www.google.com/finance/).
                    2. Use Filesystem to read the clients' documents.
                    3. Regulations will be provided as a context.
                    4. Make your decisions and write your judgement.
                    '''
        agent_orchestra['auditor'] = get_a_customized_agent(tools=auditor_tools,
                                                            system_message=auditor_system_message,
                                                            model='qwen3-next-80b-a3b-instruct')

        # Create reviewer agent.
        agent_orchestra['reviewer'] = get_a_customized_agent(tools=['add_audit_judgement'],
                                                             system_message='You are a reviewer agent who reviews the judgement of the auditor. Check whether there are conflict across the judgement of different transaction emails.',
                                                             model='qwen-max-latest')

        # Create assistant_chat agent.
        assistant_chat_tools = [
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
            'add_audit_judgement'
        ]
        assistant_chat_system_message = '''
                    You are an AI auditor of stock transactions. 
                    Make judgements according to clients' documents, market rules and client profile.
                    1. Use Playwright to search for stock information from Google finance(https://www.google.com/finance/).
                    2. Use Filesystem to read the clients' documents.
                    3. Regulations will be provided as a context.
                    4. Make your decisions and write your judgement.
                    5. Reply the human auditor's doubts in chat.
                    '''
        agent_orchestra['assistant_chat'] = get_a_customized_agent(tools=assistant_chat_tools,
                                                                   system_message=assistant_chat_system_message,
                                                                   model='qwen3-next-80b-a3b-instruct')


class FuncappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcapp'

    def ready(self):
        _initiate_agent_orchestra()

        global chat_history
        if chat_history is None:
            chat_history = QueueDict()
