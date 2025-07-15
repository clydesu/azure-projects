import azure.functions as func
import logging
import json
import os
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import uuid
from datetime import datetime

app = func.FunctionApp()

@app.route(route="process_receipt", methods=["POST"])
def process_receipt(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing receipt upload request.')
    
    try:
        # Get uploaded file
        receipt_file = req.files.get('receipt')
        if not receipt_file:
            return func.HttpResponse(
                json.dumps({"error": "No receipt file provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Generate unique filename
        file_extension = receipt_file.filename.split('.')[-1] if '.' in receipt_file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload to Blob Storage
        blob_url = upload_to_blob(receipt_file.read(), unique_filename)
        
        # Analyze with Document Intelligence
        extracted_data = analyze_receipt(blob_url)
        
        # Add metadata
        result = {
            "blob_url": blob_url,
            "processed_at": datetime.utcnow().isoformat(),
            **extracted_data
        }
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error processing receipt: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def upload_to_blob(file_data, filename):
    """Upload file to Azure Blob Storage"""
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    container_name = "receipts"
    
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(
        container=container_name, 
        blob=filename
    )
    
    blob_client.upload_blob(file_data, overwrite=True)
    return blob_client.url

def analyze_receipt(blob_url):
    """Analyze receipt using Azure Document Intelligence"""
    endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENT_INTELLIGENCE_KEY"]
    
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )
    
    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-receipt", blob_url
    )
    result = poller.result()
    
    extracted_data = {}
    
    if result.documents:
        receipt = result.documents[0]
        fields = receipt.fields
        
        # Extract common receipt fields
        if "MerchantName" in fields:
            extracted_data["merchant_name"] = fields["MerchantName"].value
            
        if "Total" in fields:
            extracted_data["total"] = str(fields["Total"].value)
            
        if "TransactionDate" in fields:
            extracted_data["date"] = str(fields["TransactionDate"].value)
            
        if "Items" in fields:
            items = []
            for item in fields["Items"].value:
                item_fields = item.value
                if "Description" in item_fields:
                    items.append(item_fields["Description"].value)
            extracted_data["items"] = items
    
    return extracted_data
