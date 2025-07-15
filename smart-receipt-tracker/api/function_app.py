import azure.functions as func
import logging
import json
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import base64
from datetime import datetime

app = func.FunctionApp()

@app.route(route="process_receipt", methods=["POST"])
def process_receipt(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing receipt upload request.')
    
    try:
        # Get the request body
        req_body = req.get_json()
        
        if not req_body or 'image_data' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "No image data provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Decode base64 image data
        image_data = base64.b64decode(req_body['image_data'])
        
        # Analyze with Document Intelligence (free tier)
        extracted_data = analyze_receipt_bytes(image_data)
        
        # Add metadata
        result = {
            "processed_at": datetime.utcnow().isoformat(),
            "status": "success",
            **extracted_data
        }
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
        
    except Exception as e:
        logging.error(f"Error processing receipt: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*"
            }
        )

@app.route(route="process_receipt", methods=["OPTIONS"])
def process_receipt_options(req: func.HttpRequest) -> func.HttpResponse:
    """Handle CORS preflight requests"""
    return func.HttpResponse(
        "",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

def analyze_receipt_bytes(image_bytes):
    """Analyze receipt using Azure Document Intelligence with direct bytes"""
    # These will be set as environment variables in Static Web Apps
    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or not key:
        return {"error": "Document Intelligence not configured"}
    
    try:
        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        # Analyze document from bytes (no blob storage needed!)
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-receipt", 
            document=image_bytes
        )
        result = poller.result()
        
        extracted_data = {
            "merchant_name": "Unknown",
            "total": "0.00",
            "date": "Unknown",
            "items": []
        }
        
        if result.documents:
            receipt = result.documents[0]
            fields = receipt.fields
            
            # Extract common receipt fields
            if "MerchantName" in fields and fields["MerchantName"].value:
                extracted_data["merchant_name"] = str(fields["MerchantName"].value)
                
            if "Total" in fields and fields["Total"].value:
                extracted_data["total"] = str(fields["Total"].value)
                
            if "TransactionDate" in fields and fields["TransactionDate"].value:
                extracted_data["date"] = str(fields["TransactionDate"].value)
                
            if "Items" in fields and fields["Items"].value:
                items = []
                for item in fields["Items"].value:
                    item_fields = item.value
                    if "Description" in item_fields and item_fields["Description"].value:
                        items.append(str(item_fields["Description"].value))
                extracted_data["items"] = items
        
        return extracted_data
        
    except Exception as e:
        logging.error(f"Document Intelligence error: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}
