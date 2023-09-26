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

jwt_secret_key = "taipei-day-trip"

booking = Blueprint("booking", __name__)

@booking.route("/api/booking", methods=['GET'])
def get_bookingData():
        # conn = pool.get_connection()
        # cursor = conn.cursor(dictionary=True)

        auth_header = request.headers.get("Authorization")
        return auth_header
        print(auth_header)
        try:
            token=auth_header.split(" ")[1]
            print("token : "+token)
        except Exception as e:
            print(e)