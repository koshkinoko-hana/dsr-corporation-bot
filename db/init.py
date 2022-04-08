from mysql.connector import connect, Error, MySQLConnection


try:
    with connect(
            host="localhost",
            user="dsr_admin",
            password="dsr_admin",
            database="dsr_assist",

    ) as c:
        connection = c
except Error as e:
    print(e)


def get_connection():
    if not connection.is_connected():
        connection.reconnect()
    return connection


def query(q, tuple, one: bool = False):
    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    cursor.execute(q, tuple)
    if one:
        return cursor.fetchone()
    return cursor.fetchall()


def insert(q, tuple):
    conn = get_connection()
    cursor = conn.cursor(prepared=True)
    cursor.execute(q, tuple)
    conn.commit()
    cursor.execute('SELECT  currval from sequences;')
    res = cursor.fetchone()
    return res[0]
