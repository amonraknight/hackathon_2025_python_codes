from django.apps import AppConfig
from agent.bot import get_a_customized_agent
from dotenv import load_dotenv
from utils.constants import *


auditor_agent = None


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
                'get_target_email',
                'register_an_email'
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
