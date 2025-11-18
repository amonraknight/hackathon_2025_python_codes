from django.apps import AppConfig
from agent.bot import get_a_customized_agent
from dotenv import load_dotenv

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
                            "D:\\hackathon_io\\outputs"
                        ]
                    },
                    "playwright": {
                        "command": "npx",
                        "args": [
                            "@playwright/mcp@latest"
                        ]
                    }
                }
                }
            ]
            system_message = '''
            你是一个交易审核智能体，通过你拥有的工具获得交易信息、文件，根据交易规则和用户画像判断交易是否合规。
            
            '''
            auditor_agent = get_a_customized_agent(tools=tools, system_message=system_message)

