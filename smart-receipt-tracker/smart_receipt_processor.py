"""
Smart Receipt Processor - Azure Document Intelligence Integration
All-in-one file for processing receipts using Azure Document Intelligence
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
    endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
    key = os.environ["DOCUMENT_INTELLIGENCE_KEY"]
    return DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Process single receipt
def process_receipt_image(image_data: bytes, filename: str = "receipt.jpg"):
    client = create_document_intelligence_client()
    poller = client.begin_analyze_document(
        model_id="prebuilt-receipt",
        analyze_request=AnalyzeDocumentRequest(base64_source=base64.b64encode(image_data).decode())
    )
    result = poller.result()
    return extract_receipt_data(result, filename)

# Process multiple receipts
def process_multiple_receipts(images_data):
    results = []
    for image_info in images_data:
        image_data = image_info['data']
        filename = image_info.get('filename', 'unknown.jpg')
        receipt_data = process_receipt_image(image_data, filename)
        receipt_data['filename'] = filename
        results.append(receipt_data)
    return {"results": results}

# Extract data from Document Intelligence result
def extract_receipt_data(result, filename):
    document = result.documents[0]
    fields = document.fields or {}
    return {
        "filename": filename,
        "merchant_name": str(fields.get("MerchantName").value) if fields.get("MerchantName") else None,
        "total": str(fields.get("Total").value) if fields.get("Total") else None,
        "date": str(fields.get("TransactionDate").value) if fields.get("TransactionDate") else None,
        "items": extract_items(fields.get("Items")),
        "confidence": getattr(document, 'confidence', 0.0)
    }

# Extract items from receipt
def extract_items(items_field):
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
