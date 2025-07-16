import os
import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_document_intelligence_client():
    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint:
        raise ValueError("DOCUMENT_INTELLIGENCE_ENDPOINT environment variable is not set. Please set it to your Azure Document Intelligence endpoint.")
    if not key:
        raise ValueError("DOCUMENT_INTELLIGENCE_KEY environment variable is not set. Please set it to your Azure Document Intelligence key.")
    if not isinstance(key, str):
        raise ValueError("DOCUMENT_INTELLIGENCE_KEY must be a string")
    
    logger.info(f"Creating client with endpoint: {endpoint}")
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    return client

def process_receipt_image(image_data: bytes, filename: str = "receipt.jpg"):
    try:
        logger.info(f"Processing receipt: {filename}")
        client = create_document_intelligence_client()
        
        logger.info(f"Starting document analysis for {filename}")
        poller = client.begin_analyze_document(
            model_id="prebuilt-receipt",
            body=image_data,
            content_type="application/octet-stream"
        )
        
        logger.info(f"Waiting for analysis results for {filename}")
        result = poller.result()
        logger.info(f"Analysis completed for {filename}")
        
        return extract_receipt_data(result, filename)
    except Exception as e:
        logger.error(f"Error processing receipt {filename}: {str(e)}")
        return {
            "filename": filename,
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "merchant_name": None,
            "total": None,
            "date": None,
            "items": []
        }

def process_multiple_receipts(images_data):
    results = []
    for image_info in images_data:
        try:
            image_data = image_info['data']
            filename = image_info.get('filename', 'unknown.jpg')
            receipt_data = process_receipt_image(image_data, filename)
            receipt_data['filename'] = filename
            results.append(receipt_data)
        except Exception as e:
            logger.error(f"Error processing image {filename}: {str(e)}")
            results.append({
                "filename": filename,
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "merchant_name": None,
                "total": None,
                "date": None,
                "items": []
            })
    
    return {"results": results}

def extract_receipt_data(result, filename):
    try:
        if not result.documents or len(result.documents) == 0:
            raise ValueError("No documents found in analysis result")
            
        document = result.documents[0]
        fields = document.fields or {}
        
        # Log available fields for debugging
        logger.info(f"Available fields in {filename}: {list(fields.keys())}")
        
        def get_field_value(field_name):
            field = fields.get(field_name)
            if field is None:
                return None
            
            try:
                # Handle different field types in the new API
                value = None
                if hasattr(field, 'content') and field.content:
                    value = str(field.content)
                elif hasattr(field, 'value_string') and field.value_string:
                    value = str(field.value_string)
                elif hasattr(field, 'value_number') and field.value_number is not None:
                    value = str(field.value_number)
                elif hasattr(field, 'value_date') and field.value_date:
                    value = str(field.value_date)
                elif hasattr(field, 'value') and field.value is not None:
                    value = str(field.value)
                else:
                    # Last resort - convert the entire field to string
                    field_str = str(field)
                    logger.info(f"Field {field_name} converted to string: {field_str}")
                    value = field_str if field_str and field_str != 'None' else None
                
                # Clean up whitespace and line breaks
                if value:
                    value = ' '.join(value.split())  # Replace multiple whitespace/newlines with single space
                    value = value.strip()
                
                return value
            except Exception as e:
                logger.warning(f"Error extracting field {field_name}: {e}")
                return None
        
        def clean_date_format(date_str):
            """Extract just the date part, remove time"""
            if not date_str:
                return None
            try:
                date_str = str(date_str).strip()
                # Handle different date formats and remove time part
                if '/' in date_str and len(date_str.split('/')) > 3:
                    # Format like "30.07.2007/13:29:17" or "12/25/2023/14:30:00"
                    parts = date_str.split('/')
                    if len(parts) >= 3:
                        # Take first 3 parts as date
                        date_part = '/'.join(parts[:3])
                        return date_part
                elif '/' in date_str:
                    # Already in MM/DD/YYYY format
                    return date_str
                elif ' ' in date_str:
                    # Format like "2023-12-25 14:30:00"
                    date_part = date_str.split(' ')[0]
                    return date_part
                else:
                    # Already just date
                    return date_str
            except Exception as e:
                logger.warning(f"Error cleaning date format '{date_str}': {e}")
                return date_str

        # Try multiple field names for date (different receipt formats)
        raw_date = (get_field_value("TransactionDate") or 
                   get_field_value("Date") or 
                   get_field_value("PurchaseDate") or
                   get_field_value("ReceiptDate"))
        
        # Clean the date to remove time
        date_value = clean_date_format(raw_date)
        
        # Get the total amount with original currency formatting
        total_amount = get_field_value("Total") or get_field_value("TotalAmount")
        
        extracted_data = {
            "filename": filename,
            "success": True,
            "merchant_name": get_field_value("MerchantName") or get_field_value("Merchant"),
            "total": total_amount,  # Keep original currency format
            "date": date_value,
            "date_of_purchase": date_value,  # Added as requested
            "items": extract_items(fields.get("Items")),
            "confidence": getattr(document, 'confidence', 0.0),
            "subtotal": get_field_value("Subtotal") or get_field_value("SubTotal"),
            "tax": get_field_value("TotalTax") or get_field_value("Tax"),
            "raw_fields": {k: str(v) for k, v in fields.items()}  # Debug: include all fields
        }
        
        logger.info(f"Extracted data for {filename}: merchant={extracted_data['merchant_name']}, total={extracted_data['total']}, date={extracted_data['date']}")
        
        return extracted_data
    except Exception as e:
        logger.error(f"Error extracting receipt data from {filename}: {str(e)}")
        return {
            "filename": filename,
            "success": False,
            "error": f"Data extraction failed: {str(e)}",
            "merchant_name": None,
            "total": None,
            "date": None,
            "date_of_purchase": None,
            "items": []
        }

def extract_items(items_field):
    items = []
    try:
        if not items_field:
            return items
            
        logger.info(f"Items field type: {type(items_field)}")
        
        # Handle different possible structures for items
        items_list = None
        if hasattr(items_field, 'value_array'):
            items_list = items_field.value_array
            logger.info(f"Found value_array with {len(items_list) if items_list else 0} items")
        elif hasattr(items_field, 'content'):
            logger.info(f"Items field content: {items_field.content}")
            # If items are in content, try to parse them
            return items  # Return empty for now if we can't parse content
        elif hasattr(items_field, 'value'):
            items_list = items_field.value
            logger.info(f"Found value with {len(items_list) if items_list else 0} items")
        else:
            logger.warning(f"Unknown items field structure: {dir(items_field)}")
            return items
            
        if not items_list:
            return items
            
        for idx, item in enumerate(items_list):
            if not item:
                continue
                
            item_data = {}
            logger.info(f"Processing item {idx}: {type(item)}")
            
            # Try to get item fields
            if hasattr(item, 'value_object') and item.value_object:
                item_fields = item.value_object
                logger.info(f"Item {idx} fields: {list(item_fields.keys()) if item_fields else 'None'}")
                
                def get_item_field(field_name):
                    field = item_fields.get(field_name)
                    if field is None:
                        return None
                    
                    value = None
                    if hasattr(field, 'content') and field.content:
                        value = str(field.content).strip()
                    elif hasattr(field, 'value_string') and field.value_string:
                        value = str(field.value_string).strip()
                    elif hasattr(field, 'value_number') and field.value_number is not None:
                        value = str(field.value_number)
                    elif hasattr(field, 'value') and field.value is not None:
                        value = str(field.value).strip()
                    else:
                        value = str(field).strip() if field else None
                    
                    logger.info(f"Field {field_name}: {value}")
                    return value
                
                # Try different possible field names for item description
                description = (get_item_field('Description') or 
                             get_item_field('Name') or 
                             get_item_field('ProductName') or
                             get_item_field('ItemName') or
                             get_item_field('Text'))
                
                # Try different possible field names for price
                price = (get_item_field('TotalPrice') or 
                        get_item_field('Price') or 
                        get_item_field('Amount') or
                        get_item_field('Cost'))
                
                quantity = get_item_field('Quantity')
                
                item_data = {
                    'description': description or f'Item {idx + 1}',
                    'total_price': price,
                    'quantity': quantity
                }
                
                logger.info(f"Extracted item {idx}: {item_data}")
                items.append(item_data)
                
    except Exception as e:
        logger.error(f"Error extracting items: {str(e)}")
    
    # Group identical items together
    grouped_items = {}
    for item in items:
        description = item.get('description', 'Item')
        price = item.get('total_price', 'N/A')
        key = f"{description}|{price}"  # Use description and price as key
        
        if key in grouped_items:
            grouped_items[key]['quantity'] += 1
        else:
            grouped_items[key] = {
                'description': description,
                'total_price': price,
                'quantity': 1,
                'original_quantity': item.get('quantity')
            }
    
    # Convert back to list format with quantity prefix
    final_items = []
    for item_data in grouped_items.values():
        quantity = item_data['quantity']
        description = item_data['description']
        
        # Format description with quantity if more than 1
        if quantity > 1:
            formatted_description = f"{quantity}x {description}"
        else:
            formatted_description = description
            
        final_items.append({
            'description': formatted_description,
            'total_price': item_data['total_price'],
            'quantity': str(quantity)
        })
    
    logger.info(f"Final grouped items: {final_items}")
    return final_items
