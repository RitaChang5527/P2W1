from flask import Flask, jsonify, request, render_template
import mysql.connector.pooling
import traceback  # 导入 traceback 模块用于错误日志记录

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

from flask import jsonify

@app.route("/api/attractions", methods=['GET'])
def get_attractions():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        page = int(request.args.get("page", 0))
        keyword = request.args.get("keyword", "")

        if not keyword:
            query = """
                SELECT a.id AS attraction_id, a.name, a.category, a.description, a.address, a.mrt, a.transport, a.latitude, a.longitude, GROUP_CONCAT(ai.image_url) AS images
                FROM attractions AS a
                LEFT JOIN attraction_images AS ai ON a.id = ai.attraction_id
                GROUP BY attraction_id, a.id  -- Include a.id in the GROUP BY clause
                LIMIT %s, 12
            """
            query_params = (page * 12, )
        else:
            query = """
                SELECT a.id AS attraction_id, a.name, a.category, a.description, a.address, a.mrt, a.transport, a.latitude, a.longitude, GROUP_CONCAT(ai.image_url) AS images
                FROM attractions AS a
                LEFT JOIN attraction_images AS ai ON a.id = ai.attraction_id
                WHERE a.name LIKE %s OR a.category = %s
                GROUP BY attraction_id, a.id  -- Include a.id in the GROUP BY clause
                ORDER BY attraction_id
                LIMIT %s OFFSET %s
            """
            query_params = (f"%{keyword}%", keyword, 12, page * 12)

        cursor.execute(query, query_params)
        attractions = cursor.fetchall()

        data_len = 12
        next_page = page + 1 if len(attractions) == data_len else None

        # Split the image URLs string into a list
        for attraction in attractions:
            image_urls = attraction.get("images", "")
            attraction["images"] = image_urls.split(",") if image_urls else []

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
        
        # Query attraction information and related image URLs
        query = """
            SELECT 
                a.id AS attractionId, a.name, a.category, a.description, a.address, a.mrt, 
                a.transport, a.latitude, a.longitude, ai.image_url AS images
            FROM attractions a
            LEFT JOIN attraction_images ai ON a.id = ai.attraction_id
            WHERE a.id = %s
        """
        cursor.execute(query, (attraction_id,))
        attraction_data = cursor.fetchone()

        if not attraction_data:
            print("Attraction data not found")
            return jsonify({"error": True, "message": "Invalid attraction ID"}), 400

        # Read the query result
        cursor.fetchall()

        # Modify field names to align with API documentation
        response_data = {
            "data": {
                "id": attraction_data["attractionId"],
                "name": attraction_data["name"],
                "category": attraction_data["category"],
                "description": attraction_data["description"],
                "address": attraction_data["address"],
                "mrt": attraction_data["mrt"],
                "transport": attraction_data["transport"],
                "latitude": attraction_data["latitude"],
                "longitude": attraction_data["longitude"],
                "images": attraction_data["images"].split(",") if attraction_data["images"] else []
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": True, "message": "Server error"}), 500
    finally:
        # Close the cursor and connection here
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
    app.run(host="0.0.0.0"port=3000)
