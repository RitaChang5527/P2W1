
from flask import *
import mysql.connector.pooling
import jwt
import datetime
import requests
from flask import make_response,jsonify

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "taipei",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="attractions_pool", pool_size=10, **db_config)
orders = Blueprint("orders", __name__)

@orders.route("/api/orders", methods=["POST"])
def payData():
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    print("connected")
    try:
        print("1")
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        decode = jwt.decode(token, "taipei-day-trip", algorithms=["HS256"])
        print(decode)
        if decode is None:
            print("None")
            return jsonify({"error": True, "message": "未登入系統，拒絕存取"}, 403)
        order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        print(order_id)
        member_id = decode["id"]
        print(member_id)

        query_history = ("SELECT * FROM orders WHERE user_id=%s;")
        cursor.execute(query_history, (member_id,))
        find_history = cursor.fetchone()
        print("222")
        if find_history != None:
            print("123")
            delete_history = ("DELETE FROM orders WHERE user_id=%s;")
            cursor.execute(delete_history, (member_id,))
            conn.commit()
        print("2222")
        try:   
            data = request.get_json()
        except Exception as e:
            print(e)
        print(data)
        order_email = data["order"]["contact"]["email"]
        print(order_email)
        order_name = data["order"]["contact"]["name"]
        print(order_name)
        order_phone = data["order"]["contact"]["phone"]
        print(order_phone)
        attraction_id = data["order"]["trip"]["attraction"]["id"]
        print(attraction_id)
        reservation_date = data["order"]["trip"]["date"]
        print(reservation_date)
        reservation_time = data["order"]["trip"]["time"]
        print(reservation_time)
        price = data["order"]["price"]
        print(price)

        query = ("INSERT INTO orders(order_id,user_id,order_name,"
                 "order_email,order_phone,attraction_id,reservation_date,"
                 "reservation_time,price,order_status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,1);")
        print("33")
        cursor.execute(query, (order_id, member_id, order_name,order_email, order_phone, attraction_id, reservation_date,reservation_time, price))
        conn.commit()
        print("333")
        # 建立傳送至第三方支付資料
        post_data = {  
            "prime": data["prime"],
            "partner_key": "partner_MnTwqDZrVTdDuOcDxl4y0tfRuWZPrvqrtf9D8ZvSmRRksBNPCdLJKeH7",
            "merchant_id": "ritachang5527_CTBC",
            "details": "taipei-day-trip",
            "order_number": order_id,
            "amount": int(data["order"]["price"]),
            "cardholder": {
                "phone_number": data["order"]["contact"]["phone"],
                "name": data["order"]["contact"]["name"],
                "email": data["order"]["contact"]["email"]
            }
        }
        print("3333" , post_data)
        headers = {
            'Content-Type': 'application/json',
            'x-api-key':'partner_MnTwqDZrVTdDuOcDxl4y0tfRuWZPrvqrtf9D8ZvSmRRksBNPCdLJKeH7'
        }
        url  = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        response = requests.post(url, headers=headers, json=post_data)
        record = response.json()
        if record["status"] == 0:
            delete_booking = ("DELETE FROM booking WHERE user_id=%s")
            cursor.execute(delete_booking, (member_id,))
            conn.commit()
            final_status = 0
            change_status = ("update orders set order_status = %s where order_id =%s;")
            cursor.execute(change_status, (final_status, order_id))
            conn.commit()
            result = {"data": {"number": "", "payment": {"status": "", "message": "付款成功"}}}
            result["data"]["number"] = order_id
            result["data"]["payment"]["status"] = final_status
            return jsonify(result), 200
        else:
            return jsonify({"error": True, "message": "訂單建立失敗，付款失敗，請重新輸入"}), 400
    except:
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        cursor.close()
        conn.close()

@orders.route("/api/orders", methods=["GET"])
def get_payData():
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    print("connected")
    try:
        result = {"data": {
            "number": "",
            "price": "",
            "trip": {
                "attraction": {
                    "id": "",
                    "name": "",
                    "address": "",
                    "image": "",
                },
                "date": "",
                "time": ""
            },
            "contact": {
                "name": "",
                "email": "",
                "phone": ""
            },
            "status": ""
        }}
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
                    orders.order_id,
                    orders.price,
                    attractions.id,
                    attractions.name,
                    attractions.address,
                    attraction_images.image_url,
                    orders.reservation_date,
                    orders.reservation_time,
                    orders.order_name,
                    orders.order_email,
                    orders.order_phone,
                    orders.order_status
                FROM
                    attractions
                INNER JOIN
                    orders ON orders.attraction_id = attractions.id
                INNER JOIN
                    attraction_images ON attractions.id = attraction_images.attraction_id
                WHERE
                    user_id = %s
            """
            print("3333")
            cursor.execute(query, (id,))
            print("33333")
            record2 = cursor.fetchone()
            while cursor.fetchone() is not None:
                pass
            print(record2)
            result["data"]["number"] = record2["order_id"]
            print(result["data"]["number"])
            result["data"]["price"] = record2["price"]
            print(result["data"]["price"])
            result["data"]["trip"]["attraction"]["id"] = record2["id"]
            print(result["data"]["trip"]["attraction"]["id"])
            result["data"]["trip"]["attraction"]["name"] = record2["name"]
            print(result["data"]["trip"]["attraction"]["name"])
            result["data"]["trip"]["attraction"]["address"] = record2["address"]
            print(result["data"]["trip"]["attraction"]["address"])
            result["data"]["trip"]["attraction"]["images"] = record2["image_url"]
            print(result["data"]["trip"]["attraction"]["images"])
            result["data"]["trip"]["date"] = record2["reservation_date"]
            print(result["data"]["trip"]["date"])
            result["data"]["trip"]["time"] = record2["reservation_time"]
            print(result["data"]["trip"]["time"])
            result["data"]["contact"]["name"] = record2["order_name"]
            print(result["data"]["contact"]["name"])
            result["data"]["contact"]["email"] = record2["order_email"]
            print(result["data"]["contact"]["email"])
            result["data"]["contact"]["phone"] = record2["order_phone"]
            print(result["data"]["contact"]["phone"])
            result["data"]["status"] = record2["order_status"]
            print(result["data"]["status"] )
            return jsonify(result)
    except:
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        if cursor:
            print("88")
            try:
                cursor.close()
            except Exception as e:
                print(e)
        if conn:
            conn.close()
            print("888")