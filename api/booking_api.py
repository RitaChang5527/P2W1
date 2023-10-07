from flask import *
import mysql.connector.pooling
import jwt
from flask import Flask, jsonify, request
from flask import Blueprint
import json 
from datetime import datetime

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "taipei",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="attractions_pool", pool_size=10, **db_config)

booking = Blueprint('booking', __name__)
@booking.route("/api/booking", methods=['GET'])
def get_bookingData():
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    print("connected")
    try:
        search = {
            "data": {
                "attraction": {
                    "id": "",
                    "name": "",
                    "address": "",
                    "image": "",
                },
                "date": "",
                "time": "",
                "price": "",
            }
        }
        
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
                        booking.book_date,
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
            record = cursor.fetchone()

            while cursor.fetchone() is not None:
                pass

            search["data"]["attraction"].update({
                "id": record["id"],
                "name": record["name"],
                "address": record["address"],
                "image": record["image_url"],
            })
            search["data"].update({
                "date": record["book_date"],
                "time": record["book_time"],
                "price": record["price"],
            })
            print("assignment:", search)

            return jsonify({'result': search})
    except:
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        print("88")
        cursor.close()
        print("888")
        conn.close()
        print("8888")

@ booking.route("/api/booking", methods=["POST"])
def create_bookingData():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("connected")
    try:
        
        print("1")
        data = request.get_json()
        print(data)
        print("11")

        attraction_id = data["attractionID"]
        print("111")
        date = data["date"]
        time = data["time"]
        price = data["price"]

        print(attraction_id)
        print(date)
        print(time)
        print(price)

        print("2")
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        decode = jwt.decode(token, "taipei-day-trip", algorithms=["HS256"])
        users_id = decode["id"]
        print("3")

        if decode == None:
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}, 403)
        elif users_id == "" or attraction_id == "" or date == "" or time == "":
            return jsonify({"error": True, "message": "輸入資料有誤，請重新點選"}, 400)
        
        else:
            print(users_id)
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
                conn.commit()

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

@ booking.route("/api/booking", methods=["DELETE"])
def delete_bookingData():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("connected")
    try:
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        print(token)
        decode = jwt.decode(token,"taipei-day-trip", algorithms=["HS256"])
        decodeID=decode["id"]
        print("3")
        if decode == None:
            print("33")
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}, 403)
        else:
            print("4")
            data = request.get_json()
            print(data)
            users_id = data["users_id"]
            print(users_id)
            print(decodeID)
            if decodeID != users_id:
                return jsonify({"error": True, "message": "登入者不同，拒絕存取"}, 403)
            else:
                print("44")
                attraction_id = data["attractionID"]
                print(attraction_id)
                # date = data["date"]
                date_str = data["date"]
                date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
                date = date_obj.strftime("%Y-%m-%d")
                print(date)
                time = data["time"]
                print(time)
                price = data["price"]
                print(price)
                queryDel = ("DELETE FROM booking WHERE user_id=%s and attraction_id=%s and book_date=%s and book_time=%s and price=%s;")
                print("4444")
                cursor.execute(queryDel, (users_id,attraction_id, date, time, price))
                print("44444")
                conn.commit()
                print("444444")
                return jsonify({"ok": True})
    except:
        return jsonify({"error": True, "message": "未登入系統，拒絕存取"}), 403
    finally:
        cursor.close()
        conn.close()