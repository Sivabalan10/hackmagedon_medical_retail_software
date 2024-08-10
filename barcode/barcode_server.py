from flask import Flask, request, jsonify,render_template
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/result')
def result():
    return render_template("result.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read image file and decode barcode
    file_stream = file.read()
    image = np.frombuffer(file_stream, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    barcodes = decode(image)
    results = []
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        results.append(barcode_data)
    print(results[0])
    return jsonify({'barcodes': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
