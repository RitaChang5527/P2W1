from flask import *
import mysql.connector.pooling
import jwt
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
    try:
        result = {"data": {"attraction": {"id": "", "name": "", "address": "", "image": ""}, "date": "", "time": "", "price": ""}}
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        decode = jwt.decode(token, "taipei-day-trip", algorithms=["HS256"])

        if decode is None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}, 403)
        else:
            id = decode["id"]
            print(id)
            query = """
                    SELECT
                        attractions.id,
                        attractions.name,
                        attractions.address,
                        attractions.images AS attraction_image,
                        DATE_FORMAT(booking.date, '%%Y-%%m-%%d') AS booking_date,
                        booking.time,
                        booking.price
                    FROM
                        attractions
                    INNER JOIN
                        booking ON booking.attraction_id = attractions.id
                    INNER JOIN
                        users ON booking.user_id = users.id
                    WHERE
                        users.id = %s
                    ORDER BY
                        booking.order_time DESC;
                """
            conn = pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (id,))
            record = cursor.fetchone()

            result["data"]["attraction"]["id"] = record["id"]
            result["data"]["attraction"]["name"] = record["name"]
            result["data"]["attraction"]["address"] = record["address"]
            result["data"]["attraction"]["image"] = record["attraction_image"]
            result["data"]["date"] = record["booking_date"]
            result["data"]["time"] = record["time"]
            result["data"]["price"] = record["price"]
            return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# @ booking.route("/api/booking", methods=["POST"])
# def create_bookingData():
#         conn = pool.get_connection()
#         cursor = conn.cursor(dictionary=True)
#         try:
#             data = request.get_json()
#             member_id = data["member_id"]
#             attraction_id = data["attractionID"]
#             date = data["date"]
#             time = data["time"]
#             price = data["price"]

#             auth_header = request.headers.get("Authorization")
#             token=auth_header.split(" ")[1]
#             decode = jwt.decode(token, "taipei-day-trip", algorithms=["HS256"])
#         if decode == None:
#             return jsonify({"error": True, "message": "未登入系統，拒絕存取"}, 403)
#         elif member_id == "" or attraction_id == "" or date == "" or time == "":
#             return jsonify({"error": True, "message": "輸入資料有誤，請重新點選"}, 400)
#         else:
#             query = ("SELECT * FROM booking WHERE member_id=%s;")
#             cursor.execute(query, (member_id,))
#             member_data = cursor.fetchone()
#             conn.commit()