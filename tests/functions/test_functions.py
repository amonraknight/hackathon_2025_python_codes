import unittest
from functions.OutLookFunctions import read_outlook_mail

class test_functions(unittest.TestCase):
    def test_outlook_download_emails(self):
        emails = read_outlook_mail("D:\\hackathon_io\\outputs")
        print(emails)

if __name__ == '__main__':
    unittest.main()