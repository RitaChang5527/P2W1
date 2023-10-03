from flask import *
import mysql.connector.pooling
import jwt
import datetime
from flask import make_response,jsonify

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "taipei",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="attractions_pool", pool_size=10, **db_config)
user = Blueprint("user", __name__)

@user.route("/api/user", methods=["POST"])
def signup():
    if request.method == "POST":
        print(request.method)
        data = request.get_json()
        print(data)
        name = data["name"]
        print(name)
        email = data["email"]
        print(email)
        password = data["password"]
        print(password)
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            print("connected")

            check_email_query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(check_email_query, (email,))
            existingEmail = cursor.fetchone()
            print(existingEmail)

            if existingEmail:
                errorResponse = jsonify({"error": True, "message": "註冊失敗，email已被註冊，請重新輸入"})
                print("error : " + str(errorResponse))
                return errorResponse, 400
            
            insertQuery = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(insertQuery, (name, email, password))
            conn.commit()

            print("ok : " + insertQuery)
            return jsonify({"ok": True}), 200
        except mysql.connector.Error as err:
            print(err)
            return jsonify({"error": "true", "message": "伺服器錯誤"}), 500
        finally:
            if conn:
                conn.close()
    else:
        return jsonify({"error": "true", "message": "伺服器錯誤"}), 500
    

@user.route("/api/user/auth", methods=["PUT"])
def login():
    if request.method == "PUT":
        try:
            data = request.get_json()
            email = data["email"]
            password = data["password"]
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            conn = pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = ("SELECT * FROM users WHERE email=%s AND password=%s")
            cursor.execute(query, (email, password))
            record = cursor.fetchone()
            if record is not None:
                id = record['id']
                name = record['name']
                email = record['email']
                payload = {
                    "id": id,
                    "name": name,
                    "email": email,
                    "exp": expiration_time
                }
                print("payload : " + str(payload))
                token = jwt.encode(payload, "taipei-day-trip", algorithm="HS256")
                response = make_response(jsonify({"ok": True, "token": token}))
                return response, 200
            else:
                print("login fail")
                result=jsonify({"error": True})
                return result
        except:
            return jsonify({"error": "true", "message": "伺服器錯誤"}), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            
@user.route("/api/user/auth", methods=["GET"])
def member():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("member connected")
    try:
        result = {"data": None}
        auth_header = request.headers.get("Authorization")
        print(auth_header)
        if auth_header is None: 
            print("notLog")
            return jsonify({"data": None})
        token = auth_header.split(" ")[1]
        if token == "null":
            print(token)
            return jsonify({"data": None})
        else:
            decode = jwt.decode(token,"taipei-day-trip", algorithms=["HS256"])
            print("login")
            id=decode['id']
            name = decode['name']
            email = decode['email']
            print("dID:", id)
            print("dName:", name)
            print("dEmail:", email)

            query = ("SELECT id,name,email FROM users WHERE id=%s AND email=%s AND name=%s")
            cursor.execute(query, (id,email, name))
            record = cursor.fetchone()
            result["data"] = record
            return jsonify(result)
    finally:
        cursor.close()
        conn.close()
        
@ user.route("/api/user/auth", methods=["DELETE"])
def signout():
    try:
        response = make_response(jsonify({"ok": True}))
        return response, 200
    except:
        return jsonify({"error": "true"}), 500


