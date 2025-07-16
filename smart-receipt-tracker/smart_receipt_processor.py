"""
Smart Receipt Processor - Azure Document Intelligence Integration
Clean, focused receipt processing using Azure Document Intelligence
"""

import os
import base64
import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Document Intelligence Configuration
def create_document_intelligence_client():
    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint:
        raise ValueError("DOCUMENT_INTELLIGENCE_ENDPOINT environment variable not set")
    if not key:
        raise ValueError("DOCUMENT_INTELLIGENCE_KEY environment variable not set")
    
    logger.info(f"Creating Document Intelligence client with endpoint: {endpoint}")
    return DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Process single receipt
def process_receipt_image(image_data: bytes, filename: str = "receipt.jpg"):
    try:
        logger.info(f"Processing receipt: {filename}, size: {len(image_data)} bytes")
        client = create_document_intelligence_client()
        
        logger.info("Sending request to Document Intelligence service")
        poller = client.begin_analyze_document(
            model_id="prebuilt-receipt",
            analyze_request=AnalyzeDocumentRequest(base64_source=base64.b64encode(image_data).decode())
        )
        
        logger.info("Waiting for analysis results")
        result = poller.result()
        
        logger.info("Processing analysis results")
        return extract_receipt_data(result, filename)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return {
            "error": str(e),
            "filename": filename,
            "success": False
        }
    except Exception as e:
        logger.error(f"Error processing receipt {filename}: {e}")
        return {
            "error": f"Failed to process receipt: {str(e)}",
            "filename": filename,
            "success": False
        }

# Process multiple receipts
def process_multiple_receipts(images_data):
    results = []
    for image_info in images_data:
        if 'error' in image_info:
            results.append({
                'filename': image_info['filename'],
                'error': image_info['error'],
                'success': False
            })
            continue
            
        image_data = image_info['data']
        filename = image_info.get('filename', 'unknown.jpg')
        receipt_data = process_receipt_image(image_data, filename)
        receipt_data['filename'] = filename
        results.append(receipt_data)
    
    return {"results": results}

# Extract data from Document Intelligence result
def extract_receipt_data(result, filename):
    try:
        if not result.documents or len(result.documents) == 0:
            logger.warning(f"No documents found in analysis result for {filename}")
            return {
                "filename": filename,
                "error": "No receipt data could be extracted from the image",
                "success": False
            }
        
        document = result.documents[0]
        fields = document.fields or {}
        
        extracted_data = {
            "filename": filename,
            "success": True,
            "merchant_name": str(fields.get("MerchantName").value) if fields.get("MerchantName") else None,
            "total": str(fields.get("Total").value) if fields.get("Total") else None,
            "date": str(fields.get("TransactionDate").value) if fields.get("TransactionDate") else None,
            "items": extract_items(fields.get("Items")),
            "confidence": getattr(document, 'confidence', 0.0)
        }
        
        logger.info(f"Successfully extracted data from {filename}")
        return extracted_data
        
    except Exception as e:
        logger.error(f"Error extracting data from {filename}: {e}")
        return {
            "filename": filename,
            "error": f"Failed to extract receipt data: {str(e)}",
            "success": False
        }

# Extract items from receipt
def extract_items(items_field):
    try:
        if not items_field or not hasattr(items_field, 'value'):
            return []
        
        items = []
        for item in items_field.value:
            item_fields = item.value
            items.append({
                'description': str(item_fields.get('Description').value) if item_fields.get('Description') else None,
                'total_price': str(item_fields.get('TotalPrice').value) if item_fields.get('TotalPrice') else None,
                'quantity': str(item_fields.get('Quantity').value) if item_fields.get('Quantity') else None
            })
        return items
    except Exception as e:
        logger.warning(f"Error extracting items: {e}")
        return []
