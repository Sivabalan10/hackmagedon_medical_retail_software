from flask import Flask, request, jsonify,render_template
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import pandas as pd

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
    file_stream = file.read()
    image = np.frombuffer(file_stream, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    barcodes = decode(image)
    results = []
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        results.append(barcode_data)


    df = pd.read_csv('ndc.csv')
    df['NDCPACKAGECODE'] = df['NDCPACKAGECODE'].str.replace('-', '')

    def verify_medicine(ndc_code):
        if ndc_code in df['NDCPACKAGECODE'].values:
            result_df = df[df['NDCPACKAGECODE'] == ndc_code]
            print("The Medicine is authentic.")
            return result_df
        else:
            print("The Medicine is not authentic.")
            return None

    def format_ndc_code(ndc_code):
        ndc_code_str = str(ndc_code)  # Convert to string if not already
        
        # Find the index of '3'
        index_of_3 = ndc_code_str.find('3')
        
        # If '3' is found, remove '3' and all characters before it
        if index_of_3 != -1:
            ndc_code_str = ndc_code_str[index_of_3 + 1:]
        
        # Remove the last character
        formatted_code = ndc_code_str[:-1]
        
        return formatted_code
    try:
    # Process the input
        ndc_code = results[0]
        print(ndc_code)
        formatted_ndc_code = format_ndc_code(ndc_code)
        print(formatted_ndc_code)
        
        result_df = verify_medicine(formatted_ndc_code)
        print(result_df)
        # Print formatted NDC code for demonstration
        print("Formatted NDC Code:", formatted_ndc_code)
        has_results = not result_df.empty
        # Render result.html template with the result dataframe
        return render_template("result.html", result=result_df ,has_results=has_results)
    except Exception as e:
        res = "Medicine Not found"
        print(e)
        return render_template("index.html",res=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
