from flask import *
import mysql.connector.pooling
import jwt
import datetime
from flask import make_response,jsonify

jwt_secret_key = "taipei-day-trip"

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
    print("123 : " + str(request.method))
    if request.method == "PUT":
        try:
            print("321")
            data = request.get_json()
            print("json : " + str(request.get_json()))
            email = data["email"]
            password = data["password"]
            print("321321")
            print("user : " + email)
            print("pwd : " + password)

            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            print("CCCCC")
            conn = pool.get_connection()
            print("connected")
            cursor = conn.cursor(dictionary=True)
            print("CCC")
            query = ("SELECT * FROM users WHERE email=%s AND password=%s")
            cursor.execute(query, (email, password))
            print("Query executed:", cursor.statement)
            record = cursor.fetchone()
            print(f"Data source: {record}")
            if record is not None:
                id = record['id']
                name = record['name']
                email = record['email']
                print("id : " + str(record['id'])) 
                print("name : " + str(record['name'])) 
                print("email : " + str(record['email'])) 
                payload = {
                    "id": id,
                    "name": name,
                    "email": email,
                    "exp": expiration_time
                }
                print("payload : " + str(payload))
                print("1")
                try:
                    token = jwt.encode(payload, "taipei-day-trip", algorithm="HS256")
                except Exception as e:
                    print(e)
                print(token)
                print("2")
                response = make_response(jsonify({"ok": True, "token": token}))
                # response.set_cookie("token", value=token, expires=expiration_time)
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
    print("member0")
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("member connected")
        result = {"data": None}
        # cookie = request.cookies
        # token = cookie.get("token")

        token=auth_header.split(" ")[1]
        print("token : "+token)
        # token = auth_header.split(" ")[1]
        # print(token)
        if token == None:
            print("data none")
            return jsonify({"data": None})
        else:
            decode = jwt.decode(token, jwt_secret_key, algorithms=["HS256"])
            print(str(decode))
            # try:
            #     decode = jwt.decode(token, "taipei-day-trip", algorithms=["HS256"])
            #     print(str(decode))
            # except Exception as e:
            #     print(e)
            name = decode['name']
            print("name : "+name)
            email = decode['email']
            print("email : " + email)

            query = ("SELECT id,name,email FROM users WHERE email=%s AND name=%s")
            cursor.execute(query, (email, name))
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
        # response.delete_cookie("token")
        return response, 200
    except:
        return jsonify({"error": "true"}), 500


