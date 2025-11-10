import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # sesuaikan kalau kamu pakai password
        database='db_sensor_iot'
    )
    return connection
