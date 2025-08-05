import os
import logging
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_document_intelligence_client():
    endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")

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

        def extract_field(field):
            if not field:
                return None
            # Try to extract value like in extract_items
            value = None
            if hasattr(field, 'content') and field.content:
                value = str(field.content).strip()
            elif hasattr(field, 'value_string') and field.value_string:
                value = str(field.value_string).strip()
            elif hasattr(field, 'value_number') and field.value_number is not None:
                value = str(field.value_number)
            elif hasattr(field, 'value_date') and field.value_date:
                value = str(field.value_date)
            elif hasattr(field, 'value_currency') and field.value_currency:
                currency = field.value_currency
                symbol = currency.get('currencySymbol', '')
                amount = currency.get('amount', '')
                try:
                    amount = f"{float(amount):.2f}"
                except Exception:
                    amount = str(amount)
                value = f"{symbol} {amount}" if symbol and amount != "" else str(currency)
            elif hasattr(field, 'value') and field.value is not None:
                value = str(field.value).strip()
            elif isinstance(field, dict):
                # Fallback for dicts
                if field.get("type") == "string":
                    val = field.get("valueString", field.get("content", str(field)))
                    value = val.replace('\n', ' ') if val else None
                elif field.get("type") == "currency":
                    currency = field.get("valueCurrency", {})
                    symbol = currency.get("currencySymbol", "")
                    amount = currency.get("amount", "")
                    try:
                        amount = f"{float(amount):.2f}"
                    except Exception:
                        amount = str(amount)
                    value = f"{symbol} {amount}" if symbol and amount != "" else field.get("content", str(field))
                elif field.get("type") == "date":
                    date_val = field.get("valueDate")
                    if date_val:
                        value = date_val.replace("-", "/")
                    else:
                        value = field.get("content", str(field))
                else:
                    value = field.get("content", str(field))
            else:
                value = str(field).strip() if field else None
            return value

        merchant_name = extract_field(fields.get("MerchantName")) or extract_field(fields.get("Merchant"))
        total = extract_field(fields.get("Total")) or extract_field(fields.get("TotalAmount"))
        date = extract_field(fields.get("TransactionDate")) or extract_field(fields.get("Date")) or extract_field(fields.get("PurchaseDate")) or extract_field(fields.get("ReceiptDate"))

        extracted_data = {
            "filename": filename,
            "success": True,
            "merchant_name": merchant_name,
            "total": total,
            "date": date,
            "items": extract_items(fields.get("Items"))
        }
        return extracted_data
    except Exception as e:
        logger.error(f"Error extracting receipt data for {filename}: {str(e)}")
        return {
            "filename": filename,
            "success": False,
            "error": f"Data extraction failed: {str(e)}",
            "merchant_name": None,
            "total": None,
            "date": None,
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