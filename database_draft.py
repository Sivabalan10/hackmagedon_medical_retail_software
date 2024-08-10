import sqlite3
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect('records.db')
cursor = conn.cursor()

# Create stock_records table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_records (
        id INTEGER PRIMARY KEY,
        last_modified TEXT,
        product_name TEXT,
        city TEXT,
        quantity INTEGER,
        total_price REAL,
        expiry_date TEXT,
        estimation_of_delivery INTEGER
    )
''')


# Create sales_records table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales_records (
        id INTEGER PRIMARY KEY,
        date TEXT,
        product_name TEXT,
        city TEXT,
        quantity_sold INTEGER,
        price REAL,
        revenue REAL,
        day_of_the_week INTEGER,
        month INTEGER,
        season TEXT,
        customer_name TEXT,
        customer_id INTEGER
    )
''')


def insert_or_update_stock_record(last_modified, product_name, city, quantity, total_price, expiry_date, estimation_of_delivery):
    cursor.execute('''
        SELECT * FROM stock_records
        WHERE product_name = ? AND city = ? AND expiry_date = ?
    ''', (product_name, city, expiry_date))
    record = cursor.fetchone()
    
    if record:
        cursor.execute('''
            UPDATE stock_records
            SET quantity = quantity + ?, total_price = total_price + ?, last_modified = ?, estimation_of_delivery = ?
            WHERE id = ?
        ''', (quantity, total_price, last_modified, estimation_of_delivery, record[0]))
    else:
        cursor.execute('''
            INSERT INTO stock_records (last_modified, product_name, city, quantity, total_price, expiry_date, estimation_of_delivery)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (last_modified, product_name, city, quantity, total_price, expiry_date, estimation_of_delivery))
    
    conn.commit()


def insert_sales_record(date, product_name, city, quantity_sold, price, customer_name, customer_id):
    revenue = quantity_sold * price
    day_of_the_week = datetime.strptime(date, "%Y-%m-%d").weekday()
    month = datetime.strptime(date, "%Y-%m-%d").month
    season = get_season(month)
    
    cursor.execute('''
        INSERT INTO sales_records (date, product_name, city, quantity_sold, price, revenue, day_of_the_week, month, season, customer_name, customer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, product_name, city, quantity_sold, price, revenue, day_of_the_week, month, season, customer_name, customer_id))
    
    conn.commit()

def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'


stock_data = [
    ("2024-08-08", "Product A", "City X", 10, 100.0, "2024-12-31", 5),
    ("2024-08-08", "Product B", "City Y", 20, 200.0, "2024-11-30", 7),
    ("2024-08-08", "Product A", "City X", 5, 50.0, "2024-12-31", 5),  
    ("2024-08-08", "Product C", "City Z", 15, 150.0, "2025-01-31", 10)
]


for data in stock_data:
    insert_or_update_stock_record(*data)


sales_data = [
    ("2024-08-01", "Product A", "City X", 5, 10.0, "Customer One", 101),
    ("2024-08-02", "Product B", "City Y", 10, 20.0, "Customer Two", 102),
    ("2024-08-03", "Product A", "City X", 2, 10.0, "Customer Three", 103),
    ("2024-08-04", "Product C", "City Z", 3, 15.0, "Customer Four", 104)
]


for data in sales_data:
    insert_sales_record(*data)

conn.close()
