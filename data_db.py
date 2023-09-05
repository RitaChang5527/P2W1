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

    # Create a dictionary to consolidate images by attraction name
    image_dict = {}

    # 遍历 JSON 数据并提取图像链接
    for spot in results:
        attraction_name = spot.get('name', '')
        images = spot.get('images', [])

        if attraction_name not in image_dict:
            image_dict[attraction_name] = images
        else:
            image_dict[attraction_name].extend(images)

    # 遍历图像字典并插入数据到数据库
    cursor = db_connection.cursor()
    for attraction_name, images in image_dict.items():
        try:
            # 检查景点是否已存在
            check_query = "SELECT id FROM attractions WHERE name = %s"
            cursor.execute(check_query, (attraction_name,))
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
                    attraction_name,
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
            for image_url in images:
                insert_image_query = (
                    "INSERT INTO attraction_images (attraction_id, image_url) "
                    "VALUES (%s, %s)"
                )

                # 插入图片链接到 attraction_images 表，并关联到对应的景点
                image_data = (attraction_id, image_url)
                cursor.execute(insert_image_query, image_data)

            # 提交更改并获取图片的 ID
            db_connection.commit()
            print("Processed Attraction:", attraction_name)
            print("Attraction ID:", attraction_id)

        except mysql.connector.Error as err:
            print("MySQL Error:", err)

finally:
    # 最后，确保关闭数据库连接
    if db_connection.is_connected():
        db_connection.close()

print("DONE")
