from flask import Flask, send_from_directory, render_template_string, request, jsonify
import os
import sys
import logging
from dotenv import load_dotenv

# Add correct module paths (use underscores, not hyphens or mixed case)
sys.path.append(os.path.join(os.path.dirname(__file__), 'seo_content_analyzer'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'smart_receipt_tracker'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import SEO Content Analyzer
try:
    from seo_content_analyzer import get_seo_insights
    logger.info("SEO Content Analyzer service imported successfully")
except ImportError as e:
    logger.error(f"Could not import SEO Content Analyzer: {e}")
    def get_seo_insights(*args, **kwargs):
        raise ImportError("seo_content_analyzer.seo_content_processor not found")

# Import Smart Receipt Tracker
try:
    from smart_receipt_tracker.smart_receipt_processor import process_receipt_image, process_multiple_receipts
    logger.info("Document Intelligence service imported successfully")
except ImportError as e:
    logger.warning(f"Document Intelligence service not available: {e}")

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'smart_receipt_tracker', '.env'))

app = Flask(__name__)

# Template for the main portfolio page
portfolio_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clyde Juan - Azure AI Projects Portfolio</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 4rem;
            position: relative;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: -50px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 100px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateX(-50%) translateY(0px); }
            50% { transform: translateX(-50%) translateY(-20px); }
        }
        
        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #fff, #f0f8ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.3rem;
            opacity: 0.95;
            margin-bottom: 1rem;
        }
        
        .header .subtitle {
            font-size: 1rem;
            opacity: 0.8;
            background: rgba(255,255,255,0.1);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            display: inline-block;
        }
        
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 2.5rem;
            margin-bottom: 4rem;
        }
        
        .project-card {
            background: linear-gradient(145deg, #ffffff, #f8f9ff);
            border-radius: 15px;
            padding: 2.5rem;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.8);
        }
        
        .project-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .project-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 25px 50px rgba(102, 126, 234, 0.25);
        }
        
        .project-card h3 {
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            font-size: 1.6rem;
            font-weight: 700;
        }
        
        .project-card p {
            margin-bottom: 2rem;
            color: #555;
            line-height: 1.6;
            font-size: 1rem;
        }
        
        .project-link {
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
            font-weight: 600;
            position: relative;
            overflow: hidden;
        }
        
        .project-link::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .project-link:hover::before {
            left: 100%;
        }
        
        .project-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .contact {
            text-align: center;
            color: white;
        }
        
        .contact a {
            color: white;
            text-decoration: none;
            margin: 0 1rem;
            font-size: 1.1rem;
        }
        
        .contact a:hover {
            text-decoration: underline;
        }
        
        .floating-contact-navbar {
            padding: 4px 10px;
            gap: 8px;
            border-radius: 16px;
            display: flex;
            background: rgba(102,126,234,0.13);
            position: fixed;
            bottom: 18px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 999;
        }
        .floating-contact-navbar a {
            display: flex;
            align-items: center;
            padding: 4px;
            border-radius: 50%;
            transition: background 0.2s;
        }
        .floating-contact-navbar a:hover {
            background: rgba(255,255,255,0.12);
        }
        .floating-contact-navbar img {
            width: 20px;
            height: 20px;
            transition: filter 0.2s;
        }
        .floating-contact-navbar a:hover img {
            filter: brightness(1.2) saturate(120%);
        }
        @media (max-width: 600px) {
            .floating-contact-navbar {
                flex-direction: row;
                left: 50%;
                bottom: 10px;
                padding: 6px 8px;
                gap: 8px;
                transform: translateX(-50%);
            }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 1rem;
            }
            
            .projects-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Azure AI Projects Portfolio</h1>
            <p>Personal showcase of Azure AI Services</p>
            <p class="subtitle">Personal showcase • Azure AI demos • Learning-focused</p>
        </header>
        
        <div class="projects-grid">
            <div class="project-card">
                <h3>Smart Receipt Tracker</h3>
                <p>
                    Fast receipt tracking powered by Azure Document Intelligence. Upload receipts, extract key data instantly, and organize your expenses with AI-driven OCR. Supports bulk receipt processing and CSV export for easy review.
                </p>
                <a href="/smart-receipt-tracker" class="project-link">Try Live App</a>
            </div>
            
            <div class="project-card">
                <h3>SEO Content Analyzer</h3>
                <p>Transform lengthy articles into concise, actionable summaries using Azure Cognitive Services. Perfect for content creators and researchers who need quick insights.</p>
                <a href="/seo-content-analyzer" class="project-link">Try Live App</a>
            </div>
            
            <div class="project-card">
                <h3>Meeting Analyst</h3>
                <p>Convert meetings into structured insights with Azure Speech-to-Text. Automatically transcribe, analyze sentiment, and extract key action items from recordings.</p>
                <a href="/meeting-analyst" class="project-link">Discover</a>
            </div>
            
            <div class="project-card">
                <h3>Serverless Chatbot</h3>
                <p>Intelligent conversational AI built with Azure Bot Framework. Natural language understanding, context-aware responses, and seamless integration with Azure services.</p>
                <a href="/serverless-chatbot" class="project-link">Chat Now</a>
            </div>
            
            <div class="project-card">
                <h3>Image Captioning App</h3>
                <p>Automatically generate descriptive captions for images using Azure Computer Vision. Perfect for accessibility, content creation, and image analysis workflows.</p>
                <a href="/image-captioning-app" class="project-link">Try It</a>
            </div>
        </div>
    </div>

    <div class="floating-contact-navbar" style="padding:4px 10px; gap:8px; border-radius:16px; display:flex; background:rgba(102,126,234,0.13); position:fixed; bottom:18px; left:50%; transform:translateX(-50%); z-index:999;">
        <a href="https://clydejuan.me" target="_blank" title="Personal Website" style="display:flex;align-items:center;">
            <img src="https://img.icons8.com/ios-filled/20/222/domain.png" style="width:20px;height:20px;transition:filter 0.2s;">
        </a>
        <a href="https://www.linkedin.com/in/clydejuan/" target="_blank" title="LinkedIn" style="display:flex;align-items:center;">
            <img src="https://img.icons8.com/ios-filled/20/222/linkedin.png" style="width:20px;height:20px;transition:filter 0.2s;">
        </a>
        <a href="mailto:clydezjuan@gmail.com" title="Email" style="display:flex;align-items:center;">
            <img src="https://img.icons8.com/ios-filled/20/222/new-post.png" style="width:20px;height:20px;transition:filter 0.2s;">
        </a>
        <a href="https://github.com/clydesu" target="_blank" title="GitHub" style="display:flex;align-items:center;">
            <img src="https://img.icons8.com/ios-filled/20/222/github.png" style="width:20px;height:20px;transition:filter 0.2s;">
        </a>
    </div>
    <style>
    .floating-contact-navbar a:hover img {
        filter: brightness(1.2) saturate(120%);
    }
    </style>
    <script>
        // Smooth scrolling for internal links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();

                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            });
        });
    </script>
</body>
</html>
"""

# Smart Receipt Tracker template with embedded JavaScript
smart_receipt_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Receipt Tracker - Azure AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }
        
        .back-button {
            position: absolute;
            left: 30px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        
        .back-button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-50%) translateX(-3px);
        }
        
        .content {
            padding: 40px;
        }
        
        .info-note {
            background: linear-gradient(45deg, #fff3cd, #fff8e1);
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
            border-left: 4px solid #f39c12;
        }
        
        .upload-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .upload-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .upload-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-size: 1.2em;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
        }
        
        .results {
            display: none;
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(145deg, #f8fff8, #ffffff);
            border-radius: 12px;
            border-left: 5px solid #4caf50;
        }
        
        .file-input { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/" class="back-button">←</a>
            <h1>Smart Receipt Tracker</h1>
            <p>Receipt extraction using Azure Document Intelligence</p>
        </div>
        <div class="content">
            <div class="info-note">
                <strong>Live Azure Integration:</strong> This application uses Azure Document Intelligence for OCR processing. Make a fast receipt tracker with Azure Document Intelligence!
            </div>
            
            <div style="margin: 40px 0;">
                <!-- Single Receipt Upload -->
                <div style="background: #f8f9ff; padding: 25px; border-radius: 10px; margin-bottom: 20px;">
                    <h4 style="color: #667eea; margin-bottom: 15px;">Single Receipt Processing</h4>
                    <input type="file" id="receiptFile" class="file-input" accept="image/*,.pdf">
                    <button onclick="document.getElementById('receiptFile').click()" class="upload-btn">
                        Choose Single File
                    </button>
                    <button onclick="processReceipt()" class="upload-btn" id="processBtn" disabled>
                        Process Receipt
                    </button>
                </div>
                
                <!-- Multiple Receipts Upload -->
                <div style="background: #f0f8ff; padding: 25px; border-radius: 10px; margin-bottom: 20px;">
                    <h4 style="color: #667eea; margin-bottom: 15px;">Bulk Receipt Processing</h4>
                    <input type="file" id="multipleReceiptFiles" class="file-input" accept="image/*,.pdf" multiple>
                    <button onclick="document.getElementById('multipleReceiptFiles').click()" class="upload-btn">
                        Choose Multiple Files
                    </button>
                    <button onclick="processMultipleReceipts()" class="upload-btn" id="processBulkBtn" disabled>
                        Process All Receipts
                    </button>
                    <button onclick="downloadResults()" class="upload-btn" id="downloadBtn" disabled style="background: linear-gradient(45deg, #28a745, #20c997);">
                        Download Results
                    </button>
                    <div id="fileList" style="margin-top: 15px;"></div>
                </div>
            </div>
            
            <!-- Add this inside your smart_receipt_template, after the bulk and single upload sections -->
            <div style="margin: 20px 0;">
                <button onclick="resetReceipts()" class="upload-btn" style="background: linear-gradient(45deg, #dc3545, #e57373);">
                    Reset All
                </button>
            </div>
            
            <div class="loading" id="loading">
                <p>Azure AI is analyzing your receipt...</p>
            </div>
            
            <div class="results" id="results">
                <h3>Extracted Information</h3>
                <div id="resultContent"></div>
            </div>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('receiptFile');
        const multipleFileInput = document.getElementById('multipleReceiptFiles');
        const processBtn = document.getElementById('processBtn');
        const processBulkBtn = document.getElementById('processBulkBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const resultContent = document.getElementById('resultContent');
        const fileList = document.getElementById('fileList');
        
        let bulkProcessingResults = null;

        // File input event listeners
        fileInput.addEventListener('change', function() {
            processBtn.disabled = !this.files.length;
            processBtn.innerHTML = this.files.length ? `Process ${this.files[0].name}` : 'Process Receipt';
        });

        multipleFileInput.addEventListener('change', function() {
            const files = this.files;
            processBulkBtn.disabled = !files.length;
            processBulkBtn.innerHTML = files.length ? `Process ${files.length} Receipts` : 'Process All Receipts';
            
            // Display selected files
            displayFileList(files);
        });

        function displayFileList(files) {
            fileList.innerHTML = '';
            if (files.length === 0) return;
            
            const listDiv = document.createElement('div');
            listDiv.style.cssText = 'margin-top: 15px; max-height: 150px; overflow-y: auto;';
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const fileItem = document.createElement('div');
                fileItem.style.cssText = 'padding: 8px 12px; margin: 5px 0; background: white; border: 1px solid #ddd; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;';
                fileItem.innerHTML = `
                    <span style="font-weight: 500;">${file.name}</span>
                    <span style="color: #666; font-size: 0.8em;">${formatFileSize(file.size)}</span>
                `;
                listDiv.appendChild(fileItem);
            }
            fileList.appendChild(listDiv);
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        // Single receipt processing
        async function processReceipt() {
            const file = fileInput.files[0];
            if (!file) return;

            loading.style.display = 'block';
            results.style.display = 'none';
            processBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/api/process_receipt', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.error) {
                    displayError(result.error);
                } else {
                    displayResults(result);
                }
                
            } catch (error) {
                displayError('Network error: ' + error.message);
            } finally {
                loading.style.display = 'none';
                processBtn.disabled = false;
            }
        }

        // Multiple receipts processing
        async function processMultipleReceipts() {
            const files = multipleFileInput.files;
            if (!files.length) return;

            loading.style.display = 'block';
            results.style.display = 'none';
            processBulkBtn.disabled = true;

            try {
                const formData = new FormData();
                for (let i = 0; i < files.length; i++) {
                    formData.append('files', files[i]);
                }
                
                const response = await fetch('/api/process_multiple', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                bulkProcessingResults = result;
                displayBulkResults(result);
                downloadBtn.disabled = false;
                
            } catch (error) {
                displayError('Network error: ' + error.message);
            } finally {
                loading.style.display = 'none';
                processBulkBtn.disabled = false;
            }
        }

        function displayResults(data) {
            console.log('Received data:', data); // Debug: log received data
            results.style.display = 'block';
            resultContent.innerHTML = `
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h4 style="color: #667eea; margin-bottom: 12px; font-size: 1.1rem;">Receipt Analysis Results</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 12px;">
                        <div style="background: #f8f9ff; padding: 10px; border-radius: 6px; border-left: 3px solid #667eea;">
                            <strong style="color: #495057; font-size: 0.8rem;">Merchant</strong><br>
                            <span style="font-size: 0.9rem; color: #333;">${data.merchant_name || 'Not detected'}</span>
                        </div>
                        <div style="background: #f8f9ff; padding: 10px; border-radius: 6px; border-left: 3px solid #28a745;">
                            <strong style="color: #495057; font-size: 0.8rem;">Total Amount</strong><br>
                            <span style="font-size: 0.9rem; font-weight: 700; color: #28a745;">${data.total || 'Not detected'}</span>
                        </div>
                        <div style="background: #f8f9ff; padding: 10px; border-radius: 6px; border-left: 3px solid #17a2b8;">
                            <strong style="color: #495057; font-size: 0.8rem;">Date of Purchase</strong><br>
                            <span style="font-size: 0.9rem; color: #333;">${data.date_of_purchase || data.date || 'Not detected'}</span>
                        </div>
                    </div>
                    ${data.items && data.items.length > 0 ? `
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 6px;">
                            <strong style="color: #495057; font-size: 0.85rem; margin-bottom: 6px; display: block;">Items (${data.items.length}):</strong>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 4px; font-size: 0.75rem;">
                                ${data.items.slice(0, 8).map(item => `
                                    <div style="display: flex; justify-content: space-between; padding: 4px 6px; background: white; border-radius: 3px; border-left: 2px solid #e9ecef;">
                                        <span style="color: #666; flex: 1;">${(item.description || 'Item').substring(0, 25)}${(item.description || 'Item').length > 25 ? '...' : ''}</span>
                                        <span style="color: #28a745; font-weight: bold; margin-left: 8px;">${item.total_price || 'N/A'}</span>
                                    </div>
                                `).join('')}
                                ${data.items.length > 8 ? `<div style="color: #666; font-style: italic; grid-column: 1/-1; text-align: center; padding: 4px;">... and ${data.items.length - 8} more items</div>` : ''}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        function displayBulkResults(data) {
            results.style.display = 'block';
            
            let totalAmounts = {}; // Store totals by currency
            let successCount = 0;
            
            data.results.forEach(receipt => {
                if (receipt.success && receipt.total) {
                    // Extract currency and amount from strings like "CHF 54.50" or "$ 117.00"
                    const totalStr = receipt.total.trim();
                    console.log('Processing total:', totalStr); // Debug log
                    
                    // Match currency patterns: CHF 54.50, $ 117.00, USD 50.00, etc.
                    const match = totalStr.match(/([A-Z]{3}|\\$|€|£)\\s*([0-9,]+\\.?[0-9]*)/i);
                    
                    if (match) {
                        const currency = match[1] === '$' ? 'USD' : match[1];
                        const amount = parseFloat(match[2].replace(',', ''));
                        
                        if (!totalAmounts[currency]) {
                            totalAmounts[currency] = 0;
                        }
                        totalAmounts[currency] += amount;
                        console.log(`Added ${amount} ${currency}, total now: ${totalAmounts[currency]}`); // Debug log
                    }
                    successCount++;
                }
            });
            
            // Format the total amounts display
            let totalDisplay = '';
            if (Object.keys(totalAmounts).length === 0) {
                totalDisplay = '$0.00';
            } else {
                const amounts = Object.entries(totalAmounts).map(([currency, amount]) => {
                    if (currency === 'USD') {
                        return `$${amount.toFixed(2)}`;
                    } else {
                        return `${currency} ${amount.toFixed(2)}`;
                    }
                });
                totalDisplay = amounts.join(' and ');
            }
            
            let html = `
                <div style="background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px;">
                    <h4 style="margin: 0 0 5px 0; font-size: 1.1rem;">Total Amount: ${totalDisplay}</h4>
                    <p style="margin: 0; font-size: 0.85rem; opacity: 0.9;">Successfully processed: ${successCount} out of ${data.results.length} receipts</p>
                </div>
            `;
            
            data.results.forEach((receipt, index) => {
                const statusColor = receipt.success ? '#28a745' : '#dc3545';
                const statusIcon = receipt.success ? 'Success' : 'Error';
                
                html += `
                    <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid ${statusColor}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h6 style="color: #495057; margin: 0; font-size: 0.9rem;">${statusIcon} - ${receipt.filename}</h6>
                            <span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">Receipt ${index + 1}</span>
                        </div>
                        ${receipt.success ? `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; font-size: 0.85rem; margin-bottom: 8px;">
                                <div><strong>Merchant:</strong><br><span style="color: #666;">${receipt.merchant_name || 'Not detected'}</span></div>
                                <div><strong>Total:</strong><br><span style="color: #28a745; font-weight: bold;">${receipt.total || 'Not detected'}</span></div>
                                <div><strong>Date:</strong><br><span style="color: #666;">${receipt.date_of_purchase || receipt.date || 'Not detected'}</span></div>
                            </div>
                            ${receipt.items && receipt.items.length > 0 ? `
                                <div style="background: #f9f9f9; padding: 8px; border-radius: 4px; margin-top: 8px;">
                                    <strong style="font-size: 0.8rem; color: #495057;">Items (${receipt.items.length}):</strong>
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 4px; margin-top: 4px; font-size: 0.75rem;">
                                        ${receipt.items.slice(0, 6).map(item => `
                                            <div style="display: flex; justify-content: space-between; padding: 2px 4px; background: white; border-radius: 3px;">
                                                <span style="color: #666; truncate;">${(item.description || 'Item').substring(0, 20)}${(item.description || 'Item').length > 20 ? '...' : ''}</span>
                                                <span style="color: #28a745; font-weight: bold;">${item.total_price || 'N/A'}</span>
                                            </div>
                                        `).join('')}
                                        ${receipt.items.length > 6 ? `<div style="color: #666; font-style: italic; grid-column: 1/-1;">... and ${receipt.items.length - 6} more items</div>` : ''}
                                    </div>
                                </div>
                            ` : ''}
                        ` : `
                            <p style="color: #dc3545; font-size: 0.85rem; margin: 0;"><strong>Error:</strong> ${receipt.error}</p>
                        `}
                    </div>
                `;
            });
            
            resultContent.innerHTML = html;
        }

        function displayError(error) {
            results.style.display = 'block';
            results.style.borderLeftColor = '#f44336';
            resultContent.innerHTML = `
                <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; border: 1px solid #f5c6cb;">
                    <h4>Processing Error</h4>
                    <p>${error}</p>
                </div>
            `;
        }

        function downloadResults() {
            if (!bulkProcessingResults) {
                alert('No results to download');
                return;
            }

            let csvContent = "Filename,Merchant,Total,Date of Purchase,Items,Items Count\\n";
            
            bulkProcessingResults.results.forEach(receipt => {
                const merchant = (receipt.merchant_name || 'N/A').replace(/"/g, '""');
                const total = receipt.total || 'Not detected';
                const date = receipt.date_of_purchase || receipt.date || 'N/A';


                
                // Format items for CSV
                let itemsText = '';
                let itemsCount = 0;
                if (receipt.items && receipt.items.length > 0) {
                    itemsCount = receipt.items.length;
                    itemsText = receipt.items.map(item => {
                        const desc = item.description || 'Item';
                        const price = item.total_price || 'N/A';
                        // Description already includes quantity (e.g., "2x Coffee")
                        return `${desc}: ${price}`;
                    }).join('; ');
                } else {
                    itemsText = 'No items detected';
                }
                
                csvContent += `"${receipt.filename}","${merchant}","${total}","${date}","${itemsText.replace(/"/g, '""')}","${itemsCount}"\\n`;
            });

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `receipt_results_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        }

        function resetReceipts() {
            // Reset single receipt
            fileInput.value = '';
            processBtn.disabled = true;
            processBtn.innerHTML = 'Process Receipt';

            // Reset bulk receipt
            multipleFileInput.value = '';
            processBulkBtn.disabled = true;
            processBulkBtn.innerHTML = 'Process All Receipts';
            downloadBtn.disabled = true;
            bulkProcessingResults = null;

            // Clear file list and results
            fileList.innerHTML = '';
            results.style.display = 'none';
            resultContent.innerHTML = '';
        }
    </script>
</body>
</html>
"""

# SEO Content Analyzer template
seo_content_analyzer_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Content Analyzer - Azure AI</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .content {
            padding: 40px;
        }
        .info-note {
            background: linear-gradient(45deg, #fff3cd, #fff8e1);
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
            border-left: 4px solid #f39c12;
        }
        textarea {
            width: 100%;
            min-height: 120px;
            border-radius: 10px;
            border: 1px solid #ddd;
            padding: 12px;
            font-size: 1em;
            margin-bottom: 18px;
            resize: vertical;
        }
        .upload-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            margin: 5px 0;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .upload-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        .upload-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .results {
            display: none;
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(145deg, #f8fff8, #ffffff);
            border-radius: 12px;
            border-left: 5px solid #4caf50;
        }
        .try-app-btn {
            display: inline-block;
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
            font-weight: 600;
            margin-bottom: 18px;
        }
        .try-app-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.25);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="position:relative;">
            <a href="/" class="back-button" style="position:absolute;left:30px;top:32%;transform:translateY(-50%);background:rgba(255,255,255,0.2);color:white;border:none;padding:10px 20px;border-radius:25px;text-decoration:none;font-size:0.9rem;transition:all 0.3s ease;">
                ←
            </a>
            <h1>SEO Content Analyzer</h1>
            <p>Analyze your content for SEO insights using Azure AI Language</p>
        </div>
        <div class="content">
            <div class="info-note">
                <strong>How it works:</strong> Paste your content below and click Enter Content to get Key Topics, Entities, Sentiment, Readability, and actionable SEO insights powered by Azure AI Language.
            </div>
            <!-- Align Reset and Enter Content buttons horizontally -->
            <form id="seoForm" onsubmit="event.preventDefault(); analyzeContent();" style="display:flex;flex-direction:column;gap:10px;">
                <textarea id="content" placeholder="Paste your content here..."></textarea>
                <div style="display:flex;gap:12px;">
                    <button type="submit" class="upload-btn" id="analyzeBtn" style="flex:1;">Enter Content</button>
                    <button type="button" class="upload-btn" style="background:linear-gradient(45deg,#dc3545,#e57373);flex:1;" onclick="resetSEOContent()">
                        Reset
                    </button>
                </div>
            </form>
            <div class="results" id="results">
                <h3>SEO Insights</h3>
                <div id="resultContent"></div>
            </div>
        </div>
    </div>
    <script>
        async function analyzeContent() {
            const content = document.getElementById('content').value.trim();
            const btn = document.getElementById('analyzeBtn');
            const results = document.getElementById('results');
            const resultContent = document.getElementById('resultContent');
            if (!content) {
                alert('Please paste your content content.');
                return;
            }
            btn.disabled = true;
            btn.innerText = "Analyzing...";
            results.style.display = 'none';
            resultContent.innerHTML = "";
            try {
                const response = await fetch('/api/seo-insights', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content })
                });
                const data = await response.json();
                if (data.error) {
                    resultContent.innerHTML = `<div style="color:#dc3545;">${data.error}</div>`;
                } else {
                    results.style.display = 'block';
                    resultContent.innerHTML = `
                        <div style="background:#f8f9ff;padding:15px;border-radius:8px;">
                            <h4 style="color:#667eea;">SEO Content Insights</h4>
                            <ul style="list-style:none;padding:0;">
                                <li>
                                    <strong>Key Topics:</strong>
                                    <ul>
                                        ${(data.key_phrases || []).slice(0, 5).map(kp => `<li style="display:inline-block;background:#e3eafe;color:#333;padding:3px 10px;margin:2px 4px 2px 0;border-radius:12px;font-size:0.95em;">${kp}</li>`).join('')}
                                        ${data.key_phrases.length > 5 ? `<li style="display:inline;color:#888;">...and ${data.key_phrases.length - 5} more</li>` : ''}
                                    </ul>
                                </li>
                                <li>
                                    <strong>Sentiment:</strong>
                                    <span style="color:${data.sentiment === 'positive' ? '#28a745' : data.sentiment === 'negative' ? '#dc3545' : '#f39c12'};font-weight:bold;">
                                        ${data.sentiment.charAt(0).toUpperCase() + data.sentiment.slice(1)}
                                    </span>
                                    <span style="font-size:0.9em;color:#888;">
                                        (Pos: ${data.sentiment_scores?.positive?.toFixed(2)}, Neu: ${data.sentiment_scores?.neutral?.toFixed(2)}, Neg: ${data.sentiment_scores?.negative?.toFixed(2)})
                                    </span>
                                </li>
                                <li>
                                    <strong>Entities:</strong>
                                    <ul>
                                        ${(data.entities || []).slice(0, 5).map(ent => `<li style="display:inline-block;background:#f0f8e8;color:#333;padding:3px 10px;margin:2px 4px 2px 0;border-radius:12px;font-size:0.95em;">${ent}</li>`).join('')}
                                        ${data.entities.length > 5 ? `<li style="display:inline;color:#888;">...and ${data.entities.length - 5} more</li>` : ''}
                                    </ul>
                                </li>
                                <li>
                                    <strong>Readability:</strong> <span style="color:#f39c12;">${data.readability}</span>
                                    <span style="font-size:0.9em;color:#888;">(${data.readability < 60 ? "Try simpler language for a wider audience." : "Easy to read!"})</span>
                                </li>
                                <li>
                                    <strong>Grade Level:</strong> <span style="color:#f39c12;">${data.grade_level}</span>
                                    <span style="font-size:0.9em;color:#888;">(${typeof data.grade_level === "string" && data.grade_level.match(/(1[2-9]|[2-9][0-9])/)? "Try lowering for general readers." : "Good for most readers."})</span>
                                </li>
                                <li>
                                    <strong>Structure:</strong>
                                    <ul>
                                        <li>Headings: <b>${data.structure_feedback?.headings ?? 0}</b></li>
                                        <li>Bullet Points: <b>${data.structure_feedback?.bullet_points ?? 0}</b></li>
                                        <li>Short Paragraphs: <b>${data.structure_feedback?.short_paragraphs ?? 0}</b></li>
                                    </ul>
                                </li>
                                <li>
                                    <strong>Tone Consistency:</strong> ${data.tone_consistent ? "<span style='color:#28a745;'>Consistent</span>" : "<span style='color:#dc3545;'>Inconsistent</span>"}
                                </li>
                                <li>
                                    <strong>Long Sentences (&gt;25 words):</strong> <span style="color:#dc3545;">${data.long_sentences.length}</span>
                                    ${data.long_sentences.length > 0 ? `<span style="font-size:0.9em;color:#888;">Try splitting long sentences for clarity.</span>` : ""}
                                </li>
                                <li>
                                    <strong>Call to Action:</strong> ${data.call_to_action_found ? "<span style='color:#28a745;'>Found</span>" : "<span style='color:#dc3545;'>Not found. Add a clear call to action."}
                                </li>
                            </ul>
                            <hr>
                            <div style="font-size:0.98em;">
                                <b>Suggestions:</b>
                                <ul style="margin-top:4px;">
                                    ${data.readability < 60 ? "<li>Use simpler language and shorter sentences.</li>" : ""}
                                    ${data.structure_feedback?.headings === 0 ? "<li>Add headings to organize your content.</li>" : ""}
                                    ${data.structure_feedback?.bullet_points === 0 ? "<li>Use bullet points for clarity.</li>" : ""}
                                    ${!data.call_to_action_found ? "<li>Add a clear call to action (e.g., 'Contact us', 'Learn more').</li>" : ""}
                                    ${data.long_sentences.length > 0 ? "<li>Break up long sentences to improve clarity.</li>" : ""}
                                    ${data.tone_consistent === false ? "<li>Keep your tone consistent throughout the content.</li>" : ""}
                                </ul>
                            </div>
                        </div>
                    `;
                }
            } catch (err) {
                resultContent.innerHTML = `<div style="color:#dc3545;">Network error: ${err.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.innerText = "Enter Content"; // <-- Fix: restore correct button text
            }
        }

        function resetSEOContent() {
            document.getElementById('content').value = '';
            document.getElementById('resultContent').innerHTML = '';
            document.getElementById('results').style.display = 'none';
            document.getElementById('analyzeBtn').disabled = false;
            document.getElementById('analyzeBtn').innerText = "Enter Content";
        }
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def portfolio():
    return render_template_string(portfolio_template)

@app.route('/smart-receipt-tracker')
def smart_receipt_tracker():
    return render_template_string(smart_receipt_template)

@app.route('/seo-content-analyzer')
def seo_content_analyzer_alias():
    return render_template_string(seo_content_analyzer_template)

@app.route('/api/process_receipt', methods=['POST', 'OPTIONS'])
def process_receipt():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Read and process file
        image_data = file.read();
        result = process_receipt_image(image_data, file.filename);

        # Debug: log what we're sending to frontend
        logger.info(f"Sending to frontend: {result}")
        
        response = jsonify(result);
        response.headers.add('Access-Control-Allow-Origin', '*');
        return response;

    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        response = jsonify({"error": "An unexpected error occurred"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/process_multiple', methods=['POST', 'OPTIONS'])  
def process_multiple():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400

        # Prepare images data for processing
        images_data = []
        for file in files:
            if file.filename == '':
                continue
            images_data.append({
                'filename': file.filename,
                'data': file.read()
            })

        result = process_multiple_receipts(images_data);

        response = jsonify(result);
        response.headers.add('Access-Control-Allow-Origin', '*');
        return response;

    except Exception as e:
        logger.error(f"Error processing multiple receipts: {e}")
        response = jsonify({"error": "An unexpected error occurred"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/meeting-analyst')
def meeting_analyst():
    return send_from_directory('meeting-analyst', 'README.md')

@app.route('/serverless-chatbot')
def serverless_chatbot():
    return send_from_directory('serverless-chatbot', 'README.md')

@app.route('/image-captioning-app')
def image_captioning_app():
    return send_from_directory('image-captioning-app', 'README.md')

@app.route('/api/seo-insights', methods=['POST'])
def seo_insights_route():
    data = request.get_json()
    content = data.get("content", "");
    if not content:
        return jsonify({"error": "No content provided"}), 400
    try:
        insights = get_seo_insights(content)
        return jsonify(insights)
    except Exception as e:
        logger.error(f"SEO Insights error: {e}", exc_info=True)  # Add this for full traceback
        return jsonify({"error": str(e)}), 500

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)