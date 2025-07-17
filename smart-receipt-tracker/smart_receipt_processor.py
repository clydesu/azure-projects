import os
import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from smart_receipt_tracker.smart_receipt_processor import process_receipt_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_document_intelligence_client():
    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
    
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    return client

def process_receipt_image(image_data: bytes, filename: str = "receipt.jpg"):
    client = create_document_intelligence_client()
    
    poller = client.begin_analyze_document(
        model_id="prebuilt-receipt",
        body=image_data,
        content_type="application/octet-stream"
    )
    
    result = poller.result()
    return extract_receipt_data(result, filename)

def process_multiple_receipts(images_data):
    results = []
    for image_info in images_data:
        image_data = image_info['data']
        filename = image_info.get('filename', 'unknown.jpg')
        receipt_data = process_receipt_image(image_data, filename)
        receipt_data['filename'] = filename
        results.append(receipt_data)
    
    return {"results": results}

def extract_receipt_data(result, filename):
    document = result.documents[0]
    fields = document.fields or {}
    
    def get_field_value(field_name):
        field = fields.get(field_name)
        return str(field.value) if field and field.value else None
    
    extracted_data = {
        "filename": filename,
        "success": True,
        "merchant_name": get_field_value("MerchantName"),
        "total": get_field_value("Total"),
        "date": get_field_value("TransactionDate"),
        "items": extract_items(fields.get("Items")),
        "confidence": getattr(document, 'confidence', 0.0),
        "subtotal": get_field_value("Subtotal"),
        "tax": get_field_value("TotalTax")
    }
    
    return extracted_data

def extract_items(items_field):
    items = []
    for item in items_field.value:
        item_fields = item.value
        
        def get_item_field(field_name):
            field = item_fields.get(field_name)
            return str(field.value) if field and field.value else None
        
        items.append({
            'description': get_item_field('Description'),
            'total_price': get_item_field('TotalPrice'),
            'quantity': get_item_field('Quantity')
        })
                
    return items
