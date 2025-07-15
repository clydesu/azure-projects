# Azure Configuration Setup

## Required Azure App Service Configuration

To enable real receipt processing, configure these environment variables in your Azure App Service:

### Document Intelligence Settings
```
DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-doc-intelligence.cognitiveservices.azure.com/
DOCUMENT_INTELLIGENCE_KEY=your-32-character-key
```

### Storage Settings
```
STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your-key;EndpointSuffix=core.windows.net
```

### Azure Functions Settings (if using Function App)
```
AzureWebJobsStorage=DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=your-key;EndpointSuffix=core.windows.net
FUNCTIONS_EXTENSION_VERSION=~4
FUNCTIONS_WORKER_RUNTIME=python
```

## How to Get These Values

### Document Intelligence
1. Go to Azure Portal → Create Resource → AI + Machine Learning → Form Recognizer
2. Create a new Form Recognizer resource (use F0 free tier)
3. Go to Keys and Endpoint to get:
   - Endpoint URL (DOCUMENT_INTELLIGENCE_ENDPOINT)
   - Key 1 (DOCUMENT_INTELLIGENCE_KEY)

### Storage Account
1. Go to Azure Portal → Create Resource → Storage → Storage Account
2. Create a new storage account
3. Go to Access Keys to get the connection string
4. Use this for both STORAGE_CONNECTION_STRING and AzureWebJobsStorage

## Features When Configured

✅ **With Configuration:**
- Real OCR using Azure Document Intelligence
- Confidence scores for extracted data
- Receipt images stored in Azure Blob Storage
- Professional-grade receipt analysis

❌ **Without Configuration:**
- Shows demo data with fallback message
- Still functional for portfolio demonstration
- Indicates missing Azure configuration

## Cost Information

- **Document Intelligence F0:** 500 free transactions/month
- **Storage Account:** First 5GB free, then ~$0.02/GB
- **App Service Free Tier:** No additional cost

Total monthly cost for demo: **$0-2** with free tier limits
