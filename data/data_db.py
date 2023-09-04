import json
import mysql.connector

try:
    # 连接到 MySQL 数据库
    db_connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456789",
        database="taipei",
    )

    if db_connection.is_connected():
        print("成功连接到数据库")

    # 读取 JSON 文件，指定字符编码为 UTF-8
    with open("data/taipei-attractions.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
        results = data['result']['results']

    # 遍历 JSON 数据并提取图像链接
    for spot in results:
        # 获取 "file" 字段的内容
        file_content = spot.get('file', '')

        # 使用 "https://" 作为分隔符来切分字符串
        url_list = file_content.split('https://')

        # 遍历切分后的 URL 列表
        for url in url_list:
            # 如果 URL 以 ".jpg"、".jpeg" 或 ".png" 结尾，将其添加上 "https://" 前缀
            if url.lower().endswith((".jpg", ".jpeg", ".png")):
                image_url = 'https://' + url
                cursor = db_connection.cursor()

                try:
                    # 检查景点是否已存在
                    check_query = "SELECT id FROM attractions WHERE name = %s"
                    cursor.execute(check_query, (spot.get('name', ''),))
                    existing_attraction = cursor.fetchone()

                    if existing_attraction:
                        # 如果景点已存在，使用现有的 Attraction ID
                        attraction_id = existing_attraction[0]
                    else:
                        # 插入景点数据到 attractions 表
                        insert_query = (
                            "INSERT INTO attractions (name, category, description, address, transport, mrt, latitude, longitude) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        )
                        data = (
                            spot.get('name', ''),
                            spot.get('CAT', ''),
                            spot.get('description', ''),
                            spot.get('address', ''),
                            spot.get('direction', ''),
                            spot.get('MRT', ''),
                            spot.get('latitude', ''),
                            spot.get('longitude', '')
                        )
                        cursor.execute(insert_query, data)

                        # 提取插入的景点的 ID
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        attraction_id = cursor.fetchone()[0]

                    # 插入图片链接到 attraction_images 表
                    insert_image_query = (
                        "INSERT INTO attraction_images (attraction_id, image_url) "
                        "VALUES (%s, %s)"
                    )

                    # 插入图片链接到 attraction_images 表，并关联到对应的景点
                    image_data = (attraction_id, image_url)
                    cursor.execute(insert_image_query, image_data)

                    # 提交更改并获取图片的 ID
                    db_connection.commit()
                    image_id = cursor.lastrowid

                    print("Processed Attraction:", spot['name'])
                    print("Attraction ID:", attraction_id)
                    print("Image ID:", image_id)

                except mysql.connector.Error as err:
                    print("MySQL Error:", err)

                finally:
                    # 关闭游标
                    cursor.close()

    print("DONE")

except mysql.connector.Error as err:
    print("数据库连接错误:", err)

finally:
    # 最后，确保关闭数据库连接
    if db_connection.is_connected():
        db_connection.close()
