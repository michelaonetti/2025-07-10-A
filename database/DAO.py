from database.DB_connect import DBConnect
from model.product import Product


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getDateRange():

        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT distinct (order_date) from orders o order by order_date"

        cursor.execute(query)

        for row in cursor:
            results.append(row["order_date"])

        first = results[0]
        last = results[-1]

        cursor.close()
        conn.close()
        return first, last

    @staticmethod
    def getAllCategory():

        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT category_name from categories"

        cursor.execute(query)

        for row in cursor:
            results.append(row["category_name"])

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getAllProdotti():

        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * from products"

        cursor.execute(query)

        for row in cursor:
            results.append(Product(**row))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getAllNodi(category):

        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = "select distinct p.product_id , p.product_name , p.brand_id , p.category_id , p.model_year , p.list_price from categories c, products p where p.category_id =c.category_id and category_name =%s"

        cursor.execute(query, (category,))

        for row in cursor:
            results.append(Product(**row))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getAllProdottiVendutiTempo(category,start,end, map):

        conn = DBConnect.get_connection()

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT p.product_id as id, COUNT(DISTINCT oi.order_id) AS vendite
            FROM products p, order_items oi, orders o, categories c
            WHERE p.category_id =c.category_id and c.category_name= %s
              AND oi.product_id = p.product_id
              AND oi.order_id = o.order_id
              AND o.order_date BETWEEN %s AND %s
            GROUP BY p.product_id"""

        cursor.execute(query, (category,start,end))

        for row in cursor:
            results.append((map[row["id"]], row["vendite"]))
        print(len(results))
        cursor.close()
        conn.close()
        return results