"""
Smart Receipt Processor - Azure Document Intelligence Integration
Clean, focused receipt processing using Azure Document Intelligence
"""

import os
import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

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
            analyze_request=image_data
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
        
        # Safe field extraction with proper error handling
        def get_field_value(field_name):
            try:
                field = fields.get(field_name)
                if field and hasattr(field, 'value') and field.value is not None:
                    return str(field.value)
                elif field and hasattr(field, 'content') and field.content is not None:
                    return str(field.content)
                return None
            except Exception as e:
                logger.warning(f"Error extracting field {field_name}: {e}")
                return None
        
        # Extract basic receipt data
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
            try:
                if hasattr(item, 'value'):
                    item_fields = item.value
                    
                    # Safe extraction helper
                    def get_item_field(field_name):
                        try:
                            field = item_fields.get(field_name)
                            if field and hasattr(field, 'value') and field.value is not None:
                                return str(field.value)
                            elif field and hasattr(field, 'content') and field.content is not None:
                                return str(field.content)
                            return None
                        except Exception:
                            return None
                    
                    items.append({
                        'description': get_item_field('Description'),
                        'total_price': get_item_field('TotalPrice'),
                        'quantity': get_item_field('Quantity')
                    })
            except Exception as e:
                logger.warning(f"Error processing item: {e}")
                continue
                
        return items
    except Exception as e:
        logger.warning(f"Error extracting items: {e}")
        return []
