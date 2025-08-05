import os
import logging
import hashlib
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from concurrent.futures import ThreadPoolExecutor

# Configure logging - reduce verbosity for production
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Global client and cache
_client = None
_receipt_cache = {}
_MAX_CACHE_SIZE = 100

def get_client():
    """Get or create Document Intelligence client (singleton pattern)"""
    global _client
    if not _client:
        endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
        _client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    return _client

def process_receipt_image(image_data, filename="receipt.jpg"):
    """Process a single receipt with caching"""
    # Check cache first
    try:
        image_hash = hashlib.md5(image_data).hexdigest()
        if image_hash in _receipt_cache:
            return _receipt_cache[image_hash]
    except Exception:
        pass
    
    try:
        client = get_client()
        poller = client.begin_analyze_document(
            model_id="prebuilt-receipt",
            body=image_data,
            content_type="application/octet-stream"
        )
        result = poller.result()
        data = extract_receipt_data(result, filename)
        
        # Cache result
        _cache_result(image_data, data)
        return data
    except Exception as e:
        logger.error(f"Error processing receipt {filename}: {str(e)}")
        return _create_error_response(filename, str(e))

def _cache_result(image_data, result):
    """Cache a processed result"""
    try:
        image_hash = hashlib.md5(image_data).hexdigest()
        if len(_receipt_cache) >= _MAX_CACHE_SIZE:
            # Simple LRU - remove first item
            _receipt_cache.pop(next(iter(_receipt_cache)))
        _receipt_cache[image_hash] = result
    except Exception:
        pass

def process_multiple_receipts(images_data):
    """Process multiple receipts in parallel using thread pool"""
    if not images_data:
        return {"results": []}
    
    # Create processing tasks
    tasks = []
    for img in images_data:
        if isinstance(img, dict) and "data" in img:
            data = img["data"]
            name = img.get("filename", "receipt.jpg")
        else:
            data = img
            name = "receipt.jpg"
        tasks.append((data, name))
    
    # Process in parallel with thread pool (optimized for I/O bound operations)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(
            lambda args: process_receipt_image(*args),
            tasks
        ))
    
    return {"results": results}

def extract_receipt_data(result, filename):
    """Extract data from receipt with simplified logic"""
    try:
        if not result.documents or len(result.documents) == 0:
            return _create_error_response(filename, "No receipt found")
        
        document = result.documents[0]
        fields = document.fields or {}
        
        merchant_name = extract_field(fields.get("MerchantName")) or extract_field(fields.get("Merchant"))
        total = extract_field(fields.get("Total")) or extract_field(fields.get("TotalAmount"))
        date = extract_field(fields.get("TransactionDate")) or extract_field(fields.get("Date"))
        
        return {
            "filename": filename,
            "success": True,
            "merchant_name": merchant_name,
            "total": total,
            "date": date,
            "items": extract_items(fields.get("Items"))
        }
    except Exception as e:
        logger.error(f"Error extracting receipt data: {str(e)}")
        return _create_error_response(filename, f"Data extraction failed: {str(e)}")

def extract_field(field):
    """Unified field extraction for all field types"""
    if not field:
        return None
    
    # Try different field attributes in order of likelihood
    if hasattr(field, 'content') and field.content:
        return str(field.content).strip()
    if hasattr(field, 'value_string') and field.value_string:
        return str(field.value_string).strip()
    if hasattr(field, 'value_date') and field.value_date:
        return str(field.value_date)
    if hasattr(field, 'value_number') and field.value_number is not None:
        return str(field.value_number)
    if hasattr(field, 'value_currency') and field.value_currency:
        currency = field.value_currency
        symbol = currency.get('currencySymbol', '')
        amount = currency.get('amount', '')
        try:
            amount = f"{float(amount):.2f}"
        except Exception:
            amount = str(amount)
        return f"{symbol} {amount}" if symbol and amount else str(currency)
    if hasattr(field, 'value') and field.value is not None:
        return str(field.value).strip()
    if isinstance(field, dict):
        # Simplified dict handling
        if "content" in field:
            return str(field["content"]).strip()
    
    return str(field).strip() if field else None

def extract_items(items_field):
    """Extract and group receipt items with simplified logic"""
    items = []
    
    try:
        # Get items list based on field type
        items_list = None
        if hasattr(items_field, 'value_array'):
            items_list = items_field.value_array
        elif hasattr(items_field, 'value') and isinstance(items_field.value, list):
            items_list = items_field.value
            
        if not items_list:
            return items
        
        # Process each item
        for idx, item in enumerate(items_list):
            if not item or not hasattr(item, 'value_object'):
                continue
                
            fields = item.value_object
            
            # Extract item fields
            description = (extract_field(fields.get('Description')) or 
                          extract_field(fields.get('Name')) or 
                          extract_field(fields.get('ProductName')) or 
                          extract_field(fields.get('ItemName')) or 
                          f'Item {idx + 1}')
            
            price = (extract_field(fields.get('TotalPrice')) or 
                    extract_field(fields.get('Price')) or 
                    extract_field(fields.get('Amount')))
            
            quantity = extract_field(fields.get('Quantity'))
            
            items.append({
                'description': description,
                'total_price': price,
                'quantity': quantity or "1"
            })
        
        # Group identical items
        grouped = {}
        for item in items:
            key = f"{item['description']}|{item['total_price']}"
            
            if key in grouped:
                current_qty = int(grouped[key]['quantity']) if grouped[key]['quantity'].isdigit() else 1
                new_qty = int(item['quantity']) if item['quantity'].isdigit() else 1
                grouped[key]['quantity'] = str(current_qty + new_qty)
            else:
                grouped[key] = item.copy()
        
        # Format descriptions with quantity prefix
        final_items = []
        for item in grouped.values():
            qty = item['quantity']
            desc = item['description']
            
            if qty != "1" and not desc.startswith(f"{qty}x "):
                item['description'] = f"{qty}x {desc}"
            
            final_items.append(item)
        
        return final_items
    
    except Exception as e:
        logger.error(f"Error extracting items: {str(e)}")
        return items  # Return empty list on error

def _create_error_response(filename, error_message):
    """Create consistent error response"""
    return {
        "filename": filename,
        "success": False,
        "error": error_message,
        "merchant_name": None,
        "total": None,
        "date": None,
        "items": []
    }