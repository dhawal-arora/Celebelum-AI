import mysql.connector as sqltor
import config

_connection = None
_cursor = None


def get_cursor():
    global _connection, _cursor
    if _connection is None or not _connection.is_connected():
        _connection = sqltor.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
        )
        _cursor = _connection.cursor()
        print("Connected to MySQL")
    return _cursor
