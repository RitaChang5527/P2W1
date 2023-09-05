from flask import Flask, jsonify, request, render_template
import mysql.connector.pooling
import traceback 
from collections import OrderedDict
import json

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.json.ensure_ascii = False  # 解码

# 创建MySQL连接池
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
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
        keyword = request.args.get("keyword", "")  # 獲取關鍵字參數

        if not keyword:
            # 如果關鍵字為空，則不進行篩選，並按照指定的順序排序
            query = """
                SELECT 
                    a.id AS id, 
                    a.name, 
                    a.category, 
                    a.description, 
                    a.address, 
                    a.transport, 
                    a.mrt, 
                    a.latitude AS lat, 
                    a.longitude AS lng, 
                    GROUP_CONCAT(ai.image_url) AS images
                FROM attractions AS a
                LEFT JOIN attraction_images AS ai ON a.id = ai.attraction_id
                GROUP BY id, a.id  # 將 a.id 列添加到 GROUP BY 子句中
                ORDER BY id ASC  # 按ID由小到大排序
                LIMIT %s, 12
            """
            query_params = (page * 12, )
        else:
            # 如果提供了關鍵字，則根據關鍵字篩選，並按照指定的順序排序
            query = """
                SELECT 
                    a.id AS id, 
                    a.name, 
                    a.category, 
                    a.description, 
                    a.address, 
                    a.transport, 
                    a.mrt, 
                    a.latitude AS lat, 
                    a.longitude AS lng, 
                    GROUP_CONCAT(ai.image_url) AS images
                FROM attractions AS a
                LEFT JOIN attraction_images AS ai ON a.id = ai.attraction_id
                WHERE a.name LIKE %s OR a.mrt LIKE %s  # 模糊比對景點名稱和捷運站名稱
                ORDER BY id ASC  # 按ID由小到大排序
                LIMIT %s OFFSET %s
            """
            query_params = (f"%{keyword}%", f"%{keyword}%", 12, page * 12)

        cursor.execute(query, query_params)
        attractions = cursor.fetchall()

        # 将数据格式化为多行文本格式的 JSON
        formatted_data = {
            "data": [
                {
                    "id": attraction["id"],
                    "name": attraction["name"],
                    "category": attraction["category"],
                    "description": attraction["description"],
                    "address": attraction["address"],
                    "transport": attraction["transport"],
                    "mrt": attraction["mrt"],
                    "lat": float(attraction["lat"]),  # 将字符串转换为浮点数
                    "lng": float(attraction["lng"]),  # 将字符串转换为浮点数
                    "images": attraction["images"].split(",") if attraction["images"] else []
                }
                for attraction in attractions
            ]
        }

        # 使用json.dumps生成多行文本格式的JSON
        json_data = json.dumps(formatted_data, ensure_ascii=False, indent=2)

        return json_data, 200, {"Content-Type": "application/json; charset=utf-8"}

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/attraction/<attraction_id>")
def get_attraction_details(attraction_id):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                a.id AS id, a.name, a.category, a.description, a.address, a.transport, a.mrt, 
                a.latitude AS lat, a.longitude AS lng, GROUP_CONCAT(ai.image_url) AS images
            FROM attractions a
            LEFT JOIN attraction_images ai ON a.id = ai.attraction_id
            WHERE a.id = %s
        """
        cursor.execute(query, (attraction_id,))
        attraction_data = cursor.fetchone()

        if not attraction_data:
            print("Attraction data not found")
            return jsonify({"error": True, "message": "Invalid attraction ID"}), 400

        response_data = OrderedDict()
        response_data["id"] = attraction_data["id"]
        response_data["name"] = attraction_data["name"]
        response_data["category"] = attraction_data["category"]
        response_data["description"] = attraction_data["description"]
        response_data["address"] = attraction_data["address"]
        response_data["transport"] = attraction_data["transport"]
        response_data["mrt"] = attraction_data["mrt"]
        response_data["lat"] = attraction_data["lat"]
        response_data["lng"] = attraction_data["lng"]
        response_data["images"] = attraction_data["images"].split(",") if attraction_data["images"] else []

        return jsonify({"data": dict(response_data)})  # 将结果包装在 "data" 键下

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": True, "message": "Server error"}), 500
    finally:
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

# 其他路由和函数

if __name__ == "__main__":
    app.run(port=3000)
