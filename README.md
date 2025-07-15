# Smart Receipt Tracker - Azure Web App + Function App

A professional receipt processing application using Azure AI Document Intelligence and Blob Storage, deployed with Azure Web App and Function App.

## 🏗️ Architecture

- **Azure Web App**: Hosts the Flask application and frontend
- **Azure Function App**: Serverless receipt processing API
- **Azure Document Intelligence**: AI-powered OCR for receipt analysis
- **Azure Blob Storage**: Secure receipt image storage
- **GitHub Actions**: Automated CI/CD deployment

## 🚀 Features

- ✅ Real-time receipt OCR processing
- ✅ Confidence scores for extracted data
- ✅ Secure blob storage integration
- ✅ Professional UI with responsive design
- ✅ Free tier compatible (F0 Document Intelligence)
- ✅ GitHub Actions deployment

## 📁 Project Structure

```
├── app.py                          # Flask web application
├── requirements.txt                # Python dependencies
├── index.html                      # Portfolio homepage
├── smart-receipt-tracker/
│   ├── index.html                  # Receipt tracker SPA
│   └── api/
│       ├── function_app.py         # Azure Function for receipt processing
│       └── requirements.txt        # Function-specific dependencies
├── .github/workflows/              # GitHub Actions for deployment
└── AZURE_SETUP.md                 # Azure configuration guide
```

## 🔧 Configuration

The application uses Azure Application Settings:

### Required Settings
- `DOCUMENT_INTELLIGENCE_ENDPOINT`
- `DOCUMENT_INTELLIGENCE_KEY`
- `AzureWebJobsStorage`
- `FUNCTIONS_EXTENSION_VERSION`
- `FUNCTIONS_WORKER_RUNTIME`

## 🌐 Deployment

Deployed automatically via GitHub Actions to:
- Azure Web App (Flask application)
- Azure Function App (API backend)

## 💰 Cost Optimization

- Document Intelligence F0: 500 free transactions/month
- Storage Account: Free tier available
- Web App: Free tier compatible
- Function App: Consumption plan (pay-per-use)

**Estimated monthly cost: $0-5** with free tier usage

## 🧪 Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py

# Access at http://localhost:8000/smart-receipt-tracker/
```

## 📸 Demo

Upload a receipt image to see:
- Merchant name extraction
- Total amount detection
- Transaction date parsing
- Line item identification
- Confidence scores for each field

## Contact

**Portfolio**: [clydejuan.me](https://clydejuan.me)  
**LinkedIn**: [linkedin.com/in/clydesu](https://linkedin.com/in/clydesu)  
**Email**: clydezjuan@gmail.com
