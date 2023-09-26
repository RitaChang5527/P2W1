from flask import *
import mysql.connector.pooling
import jwt
import datetime
from flask import make_response

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "taipei",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="attractions_pool", pool_size=10, **db_config)

booking = Blueprint("booking", __name__)

@booking.route("/api/booking", methods=['GET'])
def get_bookingData():
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)