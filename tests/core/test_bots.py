import unittest
from dotenv import load_dotenv

from core.Bot import get_basic_bot, run_bot_with_ui, get_bot_with_tools

class TestBot(unittest.TestCase):
    def test_bot(self):
        load_dotenv()
        bot = get_basic_bot()
        run_bot_with_ui(bot)

    def test_customized_bot_1(self):
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
                }
            }
            }
        ]
        bot = get_bot_with_tools(tools)
        run_bot_with_ui(bot)

    def test_customized_bot_2(self):
        load_dotenv()
        tools = [
            {'mcpServers': {  # You can specify the MCP configuration file
                "playwright": {
                  "command": "npx",
                  "args": [
                    "@playwright/mcp@latest"
                  ]
                }
            }
            }
        ]
        bot = get_bot_with_tools(tools)
        run_bot_with_ui(bot)

if __name__ == '__main__':
    unittest.main()