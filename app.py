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




if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
