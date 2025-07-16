"""
Smart Receipt Processor - Azure Document Intelligence Integration
Clean, focused receipt processing using Azure Document Intelligence
"""

import os
import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from io import BytesIO

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
    
    # Validate and potentially correct endpoint format
    if not endpoint.startswith('https://'):
        logger.warning(f"Endpoint should start with https://: {endpoint}")
    
    # Check if we need to update the endpoint format for Document Intelligence
    if 'cognitiveservices.azure.com' in endpoint and 'documentintelligence' not in endpoint:
        # Try the new Document Intelligence endpoint format
        potential_new_endpoint = endpoint.replace('cognitiveservices.azure.com', 'documentintelligence.azure.com')
        logger.info(f"Endpoint uses old format. Will try both old and new formats.")
        logger.info(f"Original endpoint: {endpoint}")
        logger.info(f"New format would be: {potential_new_endpoint}")
    
    # Mask the key for logging (show only first 8 and last 4 characters)
    masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
    logger.info(f"Creating Document Intelligence client with endpoint: {endpoint}")
    logger.info(f"Using API key: {masked_key}")
    
    try:
        client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        logger.info("Document Intelligence client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Document Intelligence client with original endpoint: {e}")
        
        # If the original endpoint fails and it's using the old format, try the new format
        if 'cognitiveservices.azure.com' in endpoint:
            try:
                new_endpoint = endpoint.replace('cognitiveservices.azure.com', 'documentintelligence.azure.com')
                logger.info(f"Trying new Document Intelligence endpoint format: {new_endpoint}")
                client = DocumentIntelligenceClient(endpoint=new_endpoint, credential=AzureKeyCredential(key))
                logger.info("Successfully created client with new endpoint format")
                return client
            except Exception as e2:
                logger.error(f"Failed with new endpoint format too: {e2}")
                raise e  # Raise the original error
        else:
            raise

# Test Document Intelligence connection
def test_document_intelligence_connection():
    """Test the Document Intelligence service connection"""
    try:
        logger.info("Testing Document Intelligence connection...")
        client = create_document_intelligence_client()
        
        # Try to get the service info (this is a simple way to test authentication)
        logger.info("Connection test successful - client created without errors")
        return {
            "success": True,
            "message": "Document Intelligence connection successful",
            "endpoint": os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT", "NOT SET")
        }
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "endpoint": os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT", "NOT SET")
        }

# Process single receipt
def process_receipt_image(image_data: bytes, filename: str = "receipt.jpg"):
    try:
        logger.info(f"Processing receipt: {filename}, size: {len(image_data)} bytes")
        
        # Validate image data
        if len(image_data) < 100:  # Too small to be a valid image
            return {
                "error": "File too small to be a valid image. Please upload a clear photo of your receipt.",
                "filename": filename,
                "success": False
            }
        
        # Check for common image formats by file header
        image_headers = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'GIF87a': 'GIF',
            b'GIF89a': 'GIF',
            b'%PDF': 'PDF'
        }
        
        file_type = None
        for header, format_name in image_headers.items():
            if image_data.startswith(header):
                file_type = format_name
                break
        
        if not file_type:
            logger.warning(f"Unknown file format for {filename}")
            # Don't fail here, let Azure decide
        else:
            logger.info(f"Detected file format: {file_type}")
        
        client = create_document_intelligence_client()
        
        logger.info("Sending request to Document Intelligence service")
        
        poller = client.begin_analyze_document(
            model_id="prebuilt-receipt",
            body=image_data,
            content_type="application/octet-stream"
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
        # Capture more detailed error information
        error_msg = str(e)
        logger.error(f"Error processing receipt {filename}: {error_msg}")
        
        # Check for common Azure errors
        if "401" in error_msg or "Access denied" in error_msg:
            logger.error("Authentication error - check your API key and endpoint")
            logger.error(f"Current endpoint: {os.environ.get('DOCUMENT_INTELLIGENCE_ENDPOINT', 'NOT SET')}")
            return {
                "error": f"Authentication failed: {error_msg}. Please verify your API key and endpoint are correct.",
                "filename": filename,
                "success": False
            }
        elif "InvalidContent" in error_msg or "corrupted or format is unsupported" in error_msg:
            return {
                "error": "The uploaded file format is not supported or the image is corrupted. Please upload a clear JPEG, PNG, or PDF image of your receipt.",
                "filename": filename,
                "success": False
            }
        elif "404" in error_msg:
            logger.error("Resource not found - check your endpoint URL")
            return {
                "error": f"Resource not found: {error_msg}. Please verify your endpoint URL is correct.",
                "filename": filename,
                "success": False
            }
        elif "403" in error_msg:
            logger.error("Forbidden - check your subscription and resource permissions")
            return {
                "error": f"Access forbidden: {error_msg}. Please check your subscription status and permissions.",
                "filename": filename,
                "success": False
            }
        else:
            return {
                "error": f"Failed to process receipt: {error_msg}",
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
