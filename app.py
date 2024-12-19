from flask import Flask, request, jsonify
from flask_cors import CORS
from bakong_khqr import KHQR
import json
import os

# Configuration file path
CONFIG_FILE = "config.json"

# Function to load the configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {"BAKONG_TOKEN": ""}

# Function to save the configuration
def save_config(config_data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config_data, file, indent=4)

# Load initial configuration
config_data = load_config()

# Initialize KHQR instance
khqr = KHQR(config_data.get("BAKONG_TOKEN"))

app = Flask(__name__)

# Enable CORS for cross-origin requests
CORS(app)

@app.route("/")
def index():
    return "Hello, World! <br> lll"

# Route to generate QR code
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.get_json()
    try:
        qr = khqr.create_qr(
            bank_account=data.get('bank_account'),
            merchant_name=data.get('merchant_name'),
            merchant_city=data.get('merchant_city'),
            amount=data.get('amount'),
            currency=data.get('currency', 'KHR'),
            store_label=data.get('store_label'),
            phone_number=data.get('phone_number'),
            bill_number=data.get('bill_number'),
            terminal_label=data.get('terminal_label'),
            static=data.get('static', False)
        )
        return jsonify({'qr': qr}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to generate a Deeplink
@app.route('/generate_deeplink', methods=['POST'])
def generate_deeplink():
    data = request.get_json()
    try:
        deeplink = khqr.generate_deeplink(
            data.get('qr'),
            callback=data.get('callback'),
            appIconUrl=data.get('appIconUrl'),
            appName=data.get('appName')
        )
        return jsonify({'deeplink': deeplink}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to generate MD5 hash
@app.route('/generate_md5', methods=['POST'])
def generate_md5():
    data = request.get_json()
    try:
        md5 = khqr.generate_md5(data.get('qr'))
        return jsonify({'md5': md5}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to check payment status
@app.route('/check_payment', methods=['POST'])
def check_payment():
    data = request.get_json()
    try:
        payment_status = khqr.check_payment(data.get('md5'))
        return jsonify({'status': payment_status}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to check bulk payments
@app.route('/check_bulk_payments', methods=['POST'])
def check_bulk_payments():
    data = request.get_json()
    try:
        bulk_payments_status = khqr.check_bulk_payments(data.get('md5_list'))
        return jsonify({'paid_transactions': bulk_payments_status}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route to update BAKONG_TOKEN
@app.route('/update_token', methods=['POST'])
def update_token():
    data = request.get_json()
    try:
        new_token = data.get("BAKONG_TOKEN")
        if not new_token:
            return jsonify({'error': 'BAKONG_TOKEN is required'}), 400
        
        # Update and save the configuration
        config_data["BAKONG_TOKEN"] = new_token
        save_config(config_data)
        
        # Reinitialize KHQR instance with new token
        global khqr
        khqr = KHQR(new_token)
        
        return jsonify({'message': 'Token updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
