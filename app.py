import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all domains

@app.route('/')
def serve_index():
    """Serve the main portfolio page"""
    return send_from_directory('.', 'index.html')

@app.route('/smart-receipt-tracker/')
def serve_receipt_tracker():
    """Serve the smart receipt tracker page"""
    return send_from_directory('smart-receipt-tracker', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    try:
        if os.path.exists(path):
            if os.path.isfile(path):
                return send_from_directory('.', path)
            elif os.path.isdir(path):
                index_path = os.path.join(path, 'index.html')
                if os.path.exists(index_path):
                    return send_from_directory(path, 'index.html')
        return "File not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/process_receipt', methods=['POST', 'OPTIONS'])
def process_receipt():
    """Handle receipt processing - demo version"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # For demo purposes, return mock data
        demo_data = {
            "status": "success",
            "merchant_name": "Demo Store (Web App Version)",
            "total": "25.99",
            "date": "2025-07-15",
            "items": ["Coffee", "Sandwich", "Tax"],
            "processed_at": "2025-07-15T12:00:00Z"
        }
        
        response = jsonify(demo_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        error_response = jsonify({"error": str(e), "status": "error"})
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return f"Internal server error: {str(error)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)