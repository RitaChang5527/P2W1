from flask import Flask, jsonify, request, render_template
import mysql.connector.pooling

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.json.ensure_ascii = False  # 解码

# 创建MySQL连接池
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "#Abc123456789",
    "database": "taipei",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="attractions_pool", pool_size=10, **db_config)

# Pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")

@app.route("/booking")
def booking():
    return render_template("booking.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/api/attractions", methods=['GET'])
def get_attractions():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        page = int(request.args.get("page", 0))
        keyword = request.args.get("keyword", "")

        if not keyword:
            query = """
                SELECT a.id AS attraction_id, a.name, a.category, a.description, a.address, a.mrt, a.transport, a.latitude, a.longitude, ai.image_url
                FROM attractions AS a
                LEFT JOIN attraction_images AS ai ON a.id = ai.attraction_id
                LIMIT %s, 12
            """
            query_params = (page * 12, )
        else:
            query = """
                SELECT a.id AS attraction_id, a.name, a.category, a.description, a.address, a.mrt, a.transport, a.latitude, a.longitude, ai.image_url
                FROM attractions AS a
                LEFT JOIN attraction_images AS ai ON a.id = ai.attraction_id
                WHERE a.name LIKE %s OR a.category = %s
                ORDER BY attraction_id
                LIMIT %s OFFSET %s
            """
            query_params = (f"%{keyword}%", keyword, 12, page * 12)

        cursor.execute(query, query_params)
        attractions = cursor.fetchall()

        data_len = 12
        next_page = page + 1 if len(attractions) == data_len else None

        response_data = {"nextPage": next_page, "data": attractions}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/attraction/<attraction_id>")
def get_attraction_details(attraction_id):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询景点信息以及相关的图片链接
        query = """
            SELECT 
                a.id, a.name, a.category, a.description, a.address, a.mrt, 
                a.transport, a.latitude, a.longitude, ai.image_url
            FROM attractions a
            LEFT JOIN attraction_images ai ON a.id = ai.attraction_id
            WHERE a.id = %s
        """
        cursor.execute(query, (attraction_id,))
        attraction_data = cursor.fetchone()

        if not attraction_data:
            print("景点数据未找到")
            return jsonify({"error": True, "message": "輸入錯誤，無此 id 編號"}), 400

        # 读取查询结果
        cursor.fetchall()

        # 在这里处理查询结果
        # ...

        return jsonify({"data": attraction_data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        # 在这里关闭游标和连接
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

@app.route("/api/mrts")
def get_mrts():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT a.mrt, COUNT(ai.attraction_id) AS num_attractions
            FROM attractions a
            LEFT JOIN attraction_images ai ON a.id = ai.attraction_id
            WHERE a.mrt IS NOT NULL
            GROUP BY a.mrt
            ORDER BY num_attractions DESC
        """
        cursor.execute(query)
        mrts = [row["mrt"] for row in cursor.fetchall()]

        return jsonify({"data": mrts})
    except Exception as e:
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
