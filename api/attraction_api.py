from flask import *
import mysql.connector.pooling
import traceback 
import json
from flask import Blueprint, jsonify

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456789",
    "database": "taipei",
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="attractions_pool", pool_size=10, **db_config)

attraction = Blueprint("attraction", __name__)

@attraction.route("/api/attractions", methods=['GET'])
def get_attractions():
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        page = int(request.args.get("page", 0))
        keyword = request.args.get("keyword", "")

        if not keyword:
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
                GROUP BY a.id, a.name, a.category, a.description, a.address, a.transport, a.mrt, a.latitude, a.longitude  # 添加所有列到GROUP BY子句中
                ORDER BY id ASC  # 按ID由小到大排序
                LIMIT %s OFFSET %s
            """
            query_params = (f"%{keyword}%", f"%{keyword}%", 12, page * 12)

        cursor.execute(query, query_params)
        attractions = cursor.fetchall()
        data_len = 12
        next_page = page + 1 if len(attractions) == data_len else None

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
                    "lat": float(attraction["lat"]),
                    "lng": float(attraction["lng"]),
                    "images": attraction["images"].split(",") if attraction["images"] else []
                }
                for attraction in attractions
            ],
            "nextPage": next_page  
        }

        json_data = json.dumps(formatted_data, ensure_ascii=False, indent=2)
        return json_data, 200, {"Content-Type": "application/json; charset=utf-8"}

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    finally:
        cursor.close()
        conn.close()

@attraction.route("/api/attraction/<attraction_id>")
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
        print(attraction_data)
        if not attraction_data:
            print("Attraction data not found")
            return jsonify({"error": True, "message": "Invalid attraction ID"}), 400

        formatted_data = {
            "data": {
                "id": attraction_data["id"],
                "name": attraction_data["name"],
                "category": attraction_data["category"],
                "description": attraction_data["description"],
                "address": attraction_data["address"],
                "transport": attraction_data["transport"],
                "mrt": attraction_data["mrt"],
                "images": attraction_data["images"].split(",") if attraction_data["images"] else []
            }
        }

        json_data = json.dumps(formatted_data, ensure_ascii=False, indent=2)
        return json_data, 200, {"Content-Type": "application/json; charset=utf-8"}

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": True, "message": "Server error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()



@attraction.route("/api/mrts")
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