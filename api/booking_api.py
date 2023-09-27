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

booking = Blueprint("booking", __name__)

@booking.route("/api/booking", methods=['GET'])
def get_bookingData():
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    print("connected")
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
                        attraction_images.image_url,
                        DATE_FORMAT(booking.book_date, '%Y-%m-%d') AS booking_date,
                        booking.book_time,
                        booking.price
                    FROM
                        attractions
                    INNER JOIN
                        booking ON booking.attraction_id = attractions.id
                    INNER JOIN
                        attraction_images ON attractions.id = attraction_images.attraction_id
                    WHERE
                        user_id = %s
                    ORDER BY
                        book_time DESC;
                """
            cursor.execute(query, (id,))
            print("user_id")
            record = cursor.fetchone()
            print("11id" + id)

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

@ booking.route("/api/booking", methods=["POST"])
def create_bookingData():

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("connected")
        print("1")
        data = request.get_json()
        print("11")
        users_id = data["member_id"]
        print("111")
        attraction_id = data["attractionID"]
        date = data["date"]
        time = data["time"]
        price = data["price"]

        print(users_id)
        print(attraction_id)
        print(date)
        print(time)
        print(price)

        print("2")
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        decode = jwt.decode(token, "taipei-day-trip", algorithms=["HS256"])
        print("3")
        if decode == None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}, 403)
        elif users_id == "" or attraction_id == "" or date == "" or time == "":
            return jsonify({"error": True, "message": "輸入資料有誤，請重新點選"}, 400)
        
        else:
            print("4")
            query = ("SELECT * FROM booking WHERE user_id=%s;")
            print("44")
            cursor.execute(query, (users_id,))
            print("444")
            member_data = cursor.fetchone()
            print(member_data)
            conn.commit()

            print("5")
            #如果沒資料就創建
            if member_data == None:
                print("55")
                query_select1= ("INSERT INTO booking(user_id, attraction_id,book_date,book_time,price) VALUES ( %s, %s, %s, %s, %s);")
                print("555")
                cursor.execute(query_select1, (users_id, attraction_id, date, time, price))
                #cursor.fetchall()
                conn.commit()
                print(type(users_id))
                print(type(attraction_id))
                print(type(date))
                print(type(time))
                print(type(price))
                print("5555")
                print("55555")

                return jsonify({"ok": True})
            #有資料就刪掉覆蓋          
            else:
                print("6")
                query2 = ("DELETE FROM booking WHERE user_id=%s;")
                print("66")
                cursor.execute(query2, (users_id,))
                print("666")
                conn.commit()
                print("6666")
                query3 = ("INSERT INTO booking(user_id, attraction_id,book_date,book_time,price) VALUES ( %s, %s, %s, %s, %s);")
                cursor.execute(query3, (users_id, attraction_id, date, time, price))
                conn.commit()
                return jsonify({"ok": True})
    except:
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        print("88")
        cursor.close()
        print("888")
        conn.close()
        print("8888")