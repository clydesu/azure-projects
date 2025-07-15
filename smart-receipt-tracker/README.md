# Smart Receipt Tracker

> Upload receipt photos and let Azure AI extract the data automatically

![Azure](https://img.shields.io/badge/Azure-Free%20Tier-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-yellow)
![Python](https://img.shields.io/badge/Python-Backend-green)

## Why I Built This

I wanted to learn Azure AI services and build something practical for my portfolio. Receipt tracking is something everyone can relate to - we all have receipts we need to organize. Plus, I wanted to show I can build cloud solutions that cost $0 to run.

## What It Does

1. Upload a receipt photo
2. Azure AI reads the receipt and extracts:
   - Store name
   - Total amount
   - Date
   - List of items
3. Shows results instantly

[Screenshot of upload interface]

[Screenshot of results]

## How It Works

**Frontend**: Simple HTML/JavaScript page hosted on Azure Static Web Apps (free)
**Backend**: Python Azure Function that calls Document Intelligence API (free tier)
**AI**: Azure Cognitive Services for receipt OCR (500 pages/month free)

**Total cost**: $0/month

## Try It Live

**[Live Demo →](https://your-app-url.azurestaticapps.net)**

## Local Setup

```bash
# Clone and navigate
git clone https://github.com/YOUR-USERNAME/azure-projects.git
cd azure-projects/smart-receipt-tracker

# Install tools
npm install -g @azure/static-web-apps-cli azure-functions-core-tools

# Install Python deps
cd api && pip install -r requirements.txt && cd ..

# Run locally
swa start . --api-location api
```

Open http://localhost:4280

## Deploy to Azure

### Quick Deploy
1. Fork this repo
2. Create Azure Static Web App in portal
3. Connect to your GitHub repo
4. Create Document Intelligence resource (free tier)
5. Add environment variables in Static Web App settings:
   - `DOCUMENT_INTELLIGENCE_ENDPOINT`
   - `DOCUMENT_INTELLIGENCE_KEY`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed steps.

## What I Learned

- Azure Static Web Apps for free hosting
- Azure Functions for serverless APIs
- Document Intelligence for OCR
- GitHub Actions for CI/CD
- Cost optimization with free tiers

## Tech Stack

- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: Python Azure Functions
- **AI**: Azure Document Intelligence
- **Hosting**: Azure Static Web Apps
- **Deployment**: GitHub Actions

Simple and focused on learning Azure AI services.
