import unittest
from utils.OutLookFunctions import read_outlook_mail, send_an_email

class test_functions(unittest.TestCase):
    def test_outlook_download_emails(self):
        emails = read_outlook_mail("D:\\hackathon_io\\outputs")
        print(emails)

    def test_send_email(self):
        send_an_email(["amonra@126.com"], "Test Subject", "Test Body")

if __name__ == '__main__':
    unittest.main()