# How to Deploy This

Quick guide to get this running on Azure for free.

## What You'll Create

- **Static Web App** - Hosts your website (free)
- **Document Intelligence** - Reads receipts (500/month free)

**Total cost**: $0

## Prerequisites

- Azure account (free tier)
- GitHub account
- Azure CLI installed

## Steps

### 1. Fork This Repo
Click "Fork" on GitHub to make your own copy.

### 2. Create Azure Resources

```bash
# Login
az login

# Create resource group
az group create --name receipt-tracker --location eastus

# Create Static Web App (this will ask you to authorize GitHub)
az staticwebapp create \
  --name my-receipt-tracker \
  --resource-group receipt-tracker \
  --source https://github.com/YOUR-USERNAME/azure-projects \
  --location eastus \
  --branch main \
  --app-location "smart-receipt-tracker" \
  --api-location "smart-receipt-tracker/api"

# Create Document Intelligence
az cognitiveservices account create \
  --name receipt-reader \
  --resource-group receipt-tracker \
  --kind FormRecognizer \
  --sku F0 \
  --location eastus
```

### 3. Get Your Keys

```bash
# Get Document Intelligence endpoint and key
az cognitiveservices account show \
  --name receipt-reader \
  --resource-group receipt-tracker \
  --query "properties.endpoint"

az cognitiveservices account keys list \
  --name receipt-reader \
  --resource-group receipt-tracker \
  --query "key1"
```

### 4. Add Environment Variables

1. Go to Azure Portal
2. Find your Static Web App
3. Go to Configuration
4. Add these settings:
   - `DOCUMENT_INTELLIGENCE_ENDPOINT`: [your endpoint]
   - `DOCUMENT_INTELLIGENCE_KEY`: [your key]

### 5. Deploy

Push any change to your GitHub repo - it will auto-deploy!

## That's It!

Your app will be live at: `https://[your-app-name].azurestaticapps.net`

## Troubleshooting

**App not working?**
- Check environment variables are set
- Look at Function logs in Azure portal

**GitHub deployment failed?**
- Check the Actions tab in your GitHub repo
- Make sure the deployment token is set

Back to [README](README.md)
