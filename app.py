import os
import base64
import uuid
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Azure SDK imports
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all domains

# Azure Configuration from Function App Application Settings
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('DOCUMENT_INTELLIGENCE_ENDPOINT')
DOCUMENT_INTELLIGENCE_KEY = os.getenv('DOCUMENT_INTELLIGENCE_KEY')
# Use AzureWebJobsStorage for Function App or STORAGE_CONNECTION_STRING
BLOB_STORAGE_CONNECTION_STRING = os.getenv('AzureWebJobsStorage') or os.getenv('STORAGE_CONNECTION_STRING')
BLOB_CONTAINER_NAME = 'receipts'

# Initialize Azure clients
document_client = None
blob_service_client = None

if DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY:
    document_client = DocumentAnalysisClient(
        endpoint=DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(DOCUMENT_INTELLIGENCE_KEY)
    )

if BLOB_STORAGE_CONNECTION_STRING:
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_STORAGE_CONNECTION_STRING)
    
    # Ensure container exists
    try:
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        container_client.create_container()
    except Exception:
        pass  # Container might already exist

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
    """Handle receipt processing using Azure Document Intelligence"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Get the image data from request
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({"error": "No image data provided", "status": "error"}), 400
        
        image_data = data['image_data']
        
        # Check if Azure services are configured
        if not document_client:
            # Fallback to demo data if Azure services not configured
            demo_data = {
                "status": "success",
                "merchant_name": "Demo Store (Configure Azure Services)",
                "total": "25.99",
                "date": "2025-07-15",
                "items": ["Coffee", "Sandwich", "Tax"],
                "processed_at": datetime.now().isoformat(),
                "note": "Set DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY in App Service Configuration to use real OCR"
            }
            response = jsonify(demo_data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Upload to Blob Storage (optional, for audit trail)
        blob_url = None
        if blob_service_client:
            try:
                blob_name = f"receipts/{uuid.uuid4()}.jpg"
                blob_client = blob_service_client.get_blob_client(
                    container=BLOB_CONTAINER_NAME, 
                    blob=blob_name
                )
                blob_client.upload_blob(image_bytes, overwrite=True)
                blob_url = blob_client.url
            except AzureError as e:
                print(f"Blob storage error: {e}")
        
        # Analyze document with Document Intelligence
        poller = document_client.begin_analyze_document(
            "prebuilt-receipt", document=image_bytes
        )
        result = poller.result()
        
        # Extract receipt information
        extracted_data = extract_receipt_data(result)
        extracted_data["processed_at"] = datetime.now().isoformat()
        extracted_data["status"] = "success"
        
        if blob_url:
            extracted_data["blob_url"] = blob_url
        
        response = jsonify(extracted_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except AzureError as e:
        error_response = jsonify({
            "error": f"Azure service error: {str(e)}", 
            "status": "error"
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500
        
    except Exception as e:
        error_response = jsonify({
            "error": f"Processing error: {str(e)}", 
            "status": "error"
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500


def extract_receipt_data(analysis_result):
    """Extract structured data from Document Intelligence analysis result"""
    extracted_data = {
        "merchant_name": "Not detected",
        "total": "0.00",
        "date": "Not detected",
        "items": [],
        "confidence_scores": {}
    }
    
    for document in analysis_result.documents:
        # Extract merchant name
        if "MerchantName" in document.fields:
            field = document.fields["MerchantName"]
            if field.value:
                extracted_data["merchant_name"] = field.value
                extracted_data["confidence_scores"]["merchant_name"] = field.confidence
        
        # Extract total amount
        if "Total" in document.fields:
            field = document.fields["Total"]
            if field.value:
                extracted_data["total"] = str(field.value)
                extracted_data["confidence_scores"]["total"] = field.confidence
        
        # Extract transaction date
        if "TransactionDate" in document.fields:
            field = document.fields["TransactionDate"]
            if field.value:
                extracted_data["date"] = field.value.strftime("%Y-%m-%d")
                extracted_data["confidence_scores"]["date"] = field.confidence
        
        # Extract items
        if "Items" in document.fields:
            items_field = document.fields["Items"]
            if items_field.value:
                items = []
                for item in items_field.value:
                    if isinstance(item.value, dict):
                        if "Description" in item.value:
                            desc = item.value["Description"]
                            if desc.value:
                                items.append(desc.value)
                extracted_data["items"] = items
    
    return extracted_data

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return f"Internal server error: {str(error)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)