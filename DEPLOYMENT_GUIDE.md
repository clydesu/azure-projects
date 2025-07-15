# Smart Receipt Tracker - Deployment Guide

## Overview
Organized project structure with each project in its own folder, basic HTML design, and main Flask app outside folders.

## Project Structure
```
azure-projects/
├── app.py                          # Main Flask app (outside folders)
├── requirements.txt                 # Main app dependencies
├── templates/
│   └── index.html                  # Main portfolio page
├── smart-receipt-tracker/          # Individual project folder
│   ├── templates/
│   │   └── receipt_tracker.html   # Basic HTML (no fancy styling)
│   ├── function/
│   │   ├── function_app.py         # Azure Function code
│   │   ├── requirements.txt        # Function dependencies
│   │   └── host.json              # Function configuration
│   └── README.md                   # Project documentation
└── DEPLOYMENT_GUIDE.md            # This file
```

## Benefits of This Structure
- ✅ **Organized**: Each project has its own folder
- ✅ **Clean**: Main app.py stays outside project folders
- ✅ **Simple**: Basic HTML design, no fancy styling
- ✅ **Scalable**: Easy to add more projects
- ✅ **Maintainable**: Clear separation of concerns

## Step-by-Step Deployment

### 1. Environment Variables for Web App
Set these in your Azure App Service Configuration:
```
AZURE_FUNCTION_URL = https://your-function-app.azurewebsites.net
```

### 2. Environment Variables for Function App
Set these in your Azure Function App Configuration:
```
AZURE_STORAGE_CONNECTION_STRING = DefaultEndpointsProtocol=https;AccountName=...
DOCUMENT_INTELLIGENCE_ENDPOINT = https://your-doc-intel.cognitiveservices.azure.com/
DOCUMENT_INTELLIGENCE_KEY = your-document-intelligence-key
```

### 3. Create Blob Storage Container
In your storage account, create a container named: `receipts`

### 4. Deploy Flask Web App
From your main project directory:
```bash
# Install dependencies locally (if needed)
pip install -r requirements.txt

# Deploy to Azure App Service
# (Use your preferred method: VS Code, GitHub Actions, or Azure CLI)
```

### 5. Deploy Azure Function
From the azure_function directory:
```bash
cd azure_function

# Install Azure Functions Core Tools if not already installed
npm install -g azure-functions-core-tools@4

# Deploy the function
func azure functionapp publish your-function-app-name
```

### 6. Test the Integration
1. Visit your deployed Flask app
2. Navigate to the Smart Receipt Tracker
3. Upload a test receipt
4. Verify the extraction works

## Why This Approach is Better

### Single App Benefits:
- **Cost**: One App Service plan instead of multiple
- **Maintenance**: Single codebase for all projects  
- **User Experience**: Seamless navigation between projects
- **Deployment**: One CI/CD pipeline for the web app
- **Shared Resources**: Common CSS, templates, utilities

### When to Use Separate Apps:
- Very different technology stacks
- Different scaling requirements
- Different teams managing projects
- Strict security isolation needed

## Next Steps

1. **Deploy the current setup** - It's ready to go!
2. **Add more projects** to the same Flask app
3. **Consider adding a database** for storing receipt data
4. **Add user authentication** if needed
5. **Implement export features** (CSV, Excel, etc.)

Your approach is exactly what I'd recommend for a portfolio! 🎯
