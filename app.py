from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import random
import string


app = Flask(__name__)


USERNAME = "admin"
PASSWORD = "password"

# Function to generate OTP
def generate_secure_otp(length=6):
    characters = string.digits + string.ascii_letters
    otp = ''.join(random.SystemRandom().choice(characters) for _ in range(length))
    return otp

# Store OTP for verification (in production, use a more secure method)
otp_storage = {}

def get_db_connection():
    conn = sqlite3.connect('records.db')
    conn.row_factory = sqlite3.Row
    return conn

def check_product_quantity(product_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT product_name, quantity
        FROM stock_records
        WHERE product_name = ?
    ''', (product_name,))
    
    record = cursor.fetchone()
    
    if record:
        product_name, quantity = record
        if quantity < 15:
            low_stock_product = product_name
            print(f"Product '{low_stock_product}' has a low stock quantity: {quantity}")
            return low_stock_product
        else:
            print(f"Product '{product_name}' has sufficient stock quantity: {quantity}")
            return None
    else:
        print(f"Product '{product_name}' not found in the records.")
        return None
    
def calculate_threshold(quantity_sold, expiry_date):
    import datetime
    weightage = min(quantity_sold / 10, 10)  
    expiry_urgency = max(0, (datetime.datetime.strptime(expiry_date, '%Y-%m-%d') - datetime.datetime.now()).days / 30)
    threshold = weightage * (1 / (expiry_urgency + 1))  
    return threshold

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email == USERNAME and password == PASSWORD:
        return jsonify({'status': 'success', 'redirect': url_for('homepage')})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'})
    
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/smart_dashboard')
def smart_dashboard():
    return render_template('smart_dashboard.html')

@app.route('/add_stock', methods=['GET'])
def stock_entry_form():
    conn = get_db_connection()
    product_names = conn.execute('SELECT DISTINCT product_name FROM stock_records').fetchall()
    conn.close()
    return render_template('add_stock.html', product_names=[row['product_name'] for row in product_names])

@app.route('/add_sale', methods=['GET'])
def sale_entry_form():
    conn = get_db_connection()
    product_names = conn.execute('SELECT DISTINCT product_name FROM stock_records').fetchall()
    conn.close()
    return render_template('add_sale.html', product_names=[row['product_name'] for row in product_names])

@app.route('/get_product_names_stock', methods=['GET'])
def get_product_names_stock():
    conn = get_db_connection()
    product_names = conn.execute('SELECT DISTINCT product_name FROM stock_records').fetchall()
    conn.close()
    return jsonify([row['product_name'] for row in product_names])

@app.route('/get_product_names', methods=['GET'])
def get_product_names():
    conn = get_db_connection()
    # Fetch only products with quantity greater than zero
    product_names = conn.execute('SELECT DISTINCT product_name FROM stock_records WHERE quantity > 0').fetchall()
    conn.close()
    return jsonify([row['product_name'] for row in product_names])


@app.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.json
    product_name = data['product_name']
    city = data['city']
    quantity = int(data['quantity'])
    price = float(data['total_price'])
    total_price = quantity * price
    expiry_date = data['expiry_date']
    last_modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM stock_records
        WHERE product_name = ? AND city = ? AND expiry_date = ?
    ''', (product_name, city, expiry_date))
    record = cursor.fetchone()

    if record:
        cursor.execute('''
            UPDATE stock_records
            SET quantity = quantity + ?, total_price = total_price + ?, last_modified = ?
            WHERE id = ?
        ''', (quantity, total_price, last_modified, record['id']))
    else:
        cursor.execute('''
            INSERT INTO stock_records (last_modified, product_name, city, quantity, total_price, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (last_modified, product_name, city, quantity, total_price, expiry_date))

    conn.commit()
    records = conn.execute('SELECT * FROM stock_records').fetchall()
    conn.close()

    return jsonify(success=True, records=[{
        'product_name': record['product_name'],
        'city': record['city'],
        'quantity': record['quantity'],
        'total_price': record['total_price'],
        'expiry_date': record['expiry_date'],
        'last_modified': record['last_modified']
    } for record in records])

# sales page
@app.route('/get_product_price')
def get_product_price():
    product_name = request.args.get('product_name')
    conn = get_db_connection()
    price = conn.execute('SELECT total_price / quantity AS price FROM stock_records WHERE product_name = ? ORDER BY last_modified DESC LIMIT 1', (product_name,)).fetchone()
    conn.close()
    return jsonify({'price': price['price'] if price else None})

@app.route('/add_sale', methods=['POST'])
def add_sale():
    data = request.get_json()
    items = data['items']
    total_amount = data['totalAmount']
    date = data['date']
    city = data['city']
    customer_name = data['customer_name']
    customer_id = data['customer_id']
    day_of_week = datetime.strptime(date, '%Y-%m-%d').weekday()
    month = datetime.strptime(date, '%Y-%m-%d').month
    season = get_season(month)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check stock availability before proceeding
    for item in items:
        cursor.execute('''
            SELECT quantity FROM stock_records WHERE product_name = ?
        ''', (item['productName'],))
        stock_quantity = cursor.fetchone()

        if stock_quantity is None:
            conn.close()
            return jsonify(success=False, message=f"Product {item['productName']} not found"), 400

        if stock_quantity[0] < item['quantity']:
            conn.close()
            return jsonify(success=False, message=f"Insufficient stock for {item['productName']}"), 400

    # If all checks pass, proceed with inserting records and updating stock
    product_0 = []
    for item in items:
        # Insert the sale record
        cursor.execute('''
            INSERT INTO sales_records (date, product_name, city, quantity_sold, price, revenue, day_of_the_week, month, season, customer_name, customer_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, item['productName'], city, item['quantity'], item['price'], item['total'], day_of_week, month, season, customer_name, customer_id))
        
        # Update the stock quantity in stock_records
        cursor.execute('''
            UPDATE stock_records
            SET quantity = quantity - ?,
                total_price = total_price - (? * (total_price / quantity))
            WHERE product_name = ?
        ''', (item['quantity'], item['quantity'], item['productName']))
        
        
        product_name_to_check =  item['productName']
        low_stock_product = check_product_quantity(product_name_to_check)
        if low_stock_product:
            product_0.append(low_stock_product)
    conn.commit()
    conn.close()

    message_body = f"""\
    Just a gentle reminder to take care of your health, {customer_name}

    - {item['productName']}  - 1 before breakfast
    - {item['productName']}  - 1/2 after lunch
    - {item['productName']}  - 1 after dinner

    We're here to help you stay on track with your wellness!"""

    # Your Twilio phone number (you get this from Twilio)
    from_number = '+16188275433'

    # Get recipient's phone number from the retailer
    to_number = customer_id

    # Send the message
    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number
    )

    # -----------------------------------------------------
    if len(product_0) != 0:
        message_body2 = f"""\
        Alert!, 
        {product_0} is running Out of Stock!.

        ~ From CarestaT"""

        # Your Twilio phone number (you get this from Twilio)
        from_number2 = '+19786999293'

        # retailer number
        to_number2 = '+919597462259'
        # Send the message
        message1 = client2.messages.create(
            body=message_body2,
            from_=from_number2,
            to=to_number2
        )

    print("Message sent successfully!")
    return jsonify(success=True)



def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'
    
@app.route('/sales_records')
def s_r():
    return render_template("sales_records.html")

@app.route('/get_sales_records')
def get_sales_records():
    conn = get_db_connection()
    records = conn.execute('''
        SELECT date, product_name, city, quantity_sold, price, revenue, day_of_the_week, month, season, customer_name, customer_id
        FROM sales_records
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in records])


@app.route('/get_stock_records')
def get_stock_records():
    conn = get_db_connection()
    records = conn.execute('''
        SELECT  last_modified, product_name, city, quantity, total_price,expiry_date
        FROM stock_records
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in records])

@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

@app.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.form.get('customer_id')
    otp = generate_secure_otp()
    otp_storage[phone_number] = otp
    
    message_body = f'Your OTP is: {otp}. Please use this to verify your identity.'
    from_number = '+16188275433'

    try:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=phone_number
        )
        return jsonify({'status': 'success', 'message': 'OTP sent successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    phone_number = request.form.get('customer_id')
    user_otp = request.form.get('otp')
    actual_otp = otp_storage.get(phone_number)

    if actual_otp and user_otp == actual_otp:
        return jsonify({'status': 'success', 'message': 'OTP verified successfully!'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid OTP. Please try again.'})
    
@app.route('/get_stock_records_analytics')
def get_stock_records_analytics():
    conn = get_db_connection()
    records = conn.execute('''
        SELECT last_modified, product_name, city, quantity, total_price, expiry_date
        FROM stock_records
    ''').fetchall()
    conn.close()

    # Fetch sales data to calculate thresholds
    sales_conn = get_db_connection()
    sales_records = sales_conn.execute('''
        SELECT product_name, SUM(quantity_sold) AS total_quantity_sold
        FROM sales_records
        GROUP BY product_name
    ''').fetchall()
    sales_conn.close()
    
    sales_data = {record['product_name']: record['total_quantity_sold'] for record in sales_records}
    
    # Calculate thresholds for each stock record
    stock_records = []
    for row in records:
        product_name = row['product_name']
        quantity_sold = sales_data.get(product_name, 0)
        threshold = calculate_threshold(quantity_sold, row['expiry_date'])
        
        stock_records.append({
            'last_modified': row['last_modified'],
            'product_name': row['product_name'],
            'city': row['city'],
            'quantity': row['quantity'],
            'total_price': row['total_price'],
            'expiry_date': row['expiry_date'],
            'threshold': threshold
        })
    
    return jsonify(stock_records)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
