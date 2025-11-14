import unittest
from dotenv import load_dotenv

from src.core.Bot import get_basic_bot, run_bot_with_ui

class TestBot(unittest.TestCase):
    def test_bot(self):
        load_dotenv()
        bot = get_basic_bot()
        run_bot_with_ui(bot)

