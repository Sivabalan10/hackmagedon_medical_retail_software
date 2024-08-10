from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime


app = Flask(__name__)


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



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
