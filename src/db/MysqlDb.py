import mysql.connector


def create_a_database_on_mysql(host: str, port: str, user: str, password: str, database: str):
    """
    Create a database on MySQL.
    :param database:
    :param host:
    :param port:
    :param user:
    :param password:
    :return:
    """
    try:
        con = mysql.connector.connect(host=host, port=port, user=user, password=password)
        cursor = con.cursor()
        cursor.execute(f"CREATE DATABASE {database}")
        cursor.close()
        con.close()
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        

def connect_to_mysql(host: str, port: str, user: str, password: str, database: str):
    """
    Connect to MySQL database
    :param host:
    :param port:
    :param user:
    :param password:
    :param database:
    :return:
    """
    try:

        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return conn
    except Exception as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
