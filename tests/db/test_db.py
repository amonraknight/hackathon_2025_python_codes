import unittest
import os
from dotenv import load_dotenv
from db.MysqlDb import connect_to_mysql, create_a_database_on_mysql


class test_db(unittest.TestCase):

    def test_connect_to_mysql(self):
        load_dotenv()
        connect_to_mysql(os.getenv("MYSQL_HOST"), "3306", os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"),
                         "hackathon")


if __name__ == '__main__':
    unittest.main()
