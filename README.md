<<<<<<< HEAD
# Azure AI Projects Portfolio

Showcasing AI-powered applications built with Azure Cognitive Services and deployed via GitHub Actions.

## 🚀 Live Demo

**[clydejuan-azure-projects.azurewebsites.net](https://clydejuan-azure-projects.azurewebsites.net)**

## 🧾 Smart Receipt Tracker - Featured Project

Professional receipt processing application powered by **Azure Document Intelligence**. 

### Features
- **Real Azure Integration**: Uses Azure Document Intelligence API for production-grade OCR
- **Multiple File Support**: Process single receipts or bulk upload up to 10 receipts
- **Structured Data Extraction**: Automatically extracts merchant names, totals, dates, and itemized purchases
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Error Handling**: Robust error handling with user-friendly messages

### Technology Stack
- **Backend**: Flask (Python)
- **AI Service**: Azure Document Intelligence (prebuilt-receipt model)
- **Authentication**: Azure Key Credential + DefaultAzureCredential support
- **Deployment**: Azure App Service via GitHub Actions
- **Frontend**: Vanilla JavaScript with modern UI

### Environment Variables Required
```
DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
DOCUMENT_INTELLIGENCE_KEY=your-api-key
```

## 📁 Other Projects

- **Blog Summarizer** - AI-powered content summarization (`blog-summarizer/`)
- **Meeting Analyst** - Meeting transcription and analysis (`meeting-analyst/`)
- **Serverless Chatbot** - AI chatbot with NLP (`serverless-chatbot/`)
- **Image Captioning App** - AI-powered image descriptions (`image-captioning-app/`)

## 🛠️ Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/clydesu/azure-projects.git
   cd azure-projects
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure Document Intelligence credentials
   ```

4. **Test Document Intelligence integration**
   ```bash
   python test_document_intelligence.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## 🚀 Deployment

The application is automatically deployed to Azure App Service via GitHub Actions when changes are pushed to the main branch.

### Required Azure App Service Settings
- `DOCUMENT_INTELLIGENCE_ENDPOINT`
- `DOCUMENT_INTELLIGENCE_KEY`

## 📧 Contact

**Portfolio**: [clydejuan.me](https://clydejuan.me)  
**LinkedIn**: [linkedin.com/in/clydesu](https://linkedin.com/in/clydesu)  
**Email**: clydezjuan@gmail.com  
**GitHub**: [github.com/clydesu/azure-projects](https://github.com/clydesu/azure-projects)
=======
# azure-projects
A collection of personal projects built using Azure's free-tier services. These serve as my hands-on entry into cloud development, highlighting practical skills in deploying and managing cloud solutions as I build my foundation in the field.
>>>>>>> 08a4a19e238056393954bc92e2c99a24b5df4c22
