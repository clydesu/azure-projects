# Smart Receipt Tracker

## Overview
A serverless Azure-based application that allows users to upload receipts, automatically extract key information using Azure AI Document Intelligence, and store the results.

## Components
- **Azure Function**: Processes receipt uploads and extracts data
- **Azure Blob Storage**: Stores receipt images
- **Azure Document Intelligence**: Analyzes receipts and extracts structured data
- **Flask Web App**: Provides user interface

## Project Structure
```
smart-receipt-tracker/
├── templates/
│   └── receipt_tracker.html    # Basic HTML interface
├── function/
│   ├── function_app.py         # Azure Function code
│   ├── requirements.txt        # Function dependencies
│   └── host.json              # Function configuration
└── README.md                  # This file
```

## Setup Instructions

### 1. Azure Resources Required
- Azure Function App
- Azure Storage Account (with "receipts" container)
- Azure Document Intelligence service

### 2. Environment Variables for Function App
```
AZURE_STORAGE_CONNECTION_STRING = <your-storage-connection-string>
DOCUMENT_INTELLIGENCE_ENDPOINT = <your-doc-intel-endpoint>
DOCUMENT_INTELLIGENCE_KEY = <your-doc-intel-key>
```

### 3. Environment Variables for Web App
```
AZURE_FUNCTION_URL = <your-function-app-url>
```

### 4. Deploy Function
```bash
cd function
func azure functionapp publish <your-function-app-name>
```

## Features
- Upload receipt images (JPG, PNG, PDF)
- Extract merchant name, total amount, date, and items
- Store receipts securely in Azure Blob Storage
- Simple, clean web interface
- Serverless architecture for cost optimization

## Technology Stack
- **Backend**: Azure Functions (Python)
- **AI**: Azure Document Intelligence
- **Storage**: Azure Blob Storage
- **Frontend**: HTML/JavaScript (basic styling)
- **Web Framework**: Flask (integrated with main portfolio app)
