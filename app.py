from flask import Flask, send_from_directory, render_template_string, request, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Add smart-receipt-tracker to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'smart-receipt-tracker'))

try:
    from smart_receipt_processor import process_receipt_image, process_multiple_receipts
    logger.info("Document Intelligence service imported successfully")
except ImportError as e:
    logger.warning(f"Document Intelligence service not available: {e}")

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
            <p>Cutting-edge AI solutions powered by Microsoft Azure</p>
            <p class="subtitle">Production-ready • Real-world applications • Modern tech stack</p>
        </header>
        
        <div class="projects-grid">
            <div class="project-card">
                <h3>Smart Receipt Tracker</h3>
                <p>Intelligent expense management with Azure Document Intelligence. Upload receipts, extract data automatically, and categorize expenses with AI-powered analysis. Includes bulk processing and CSV export.</p>
                <a href="/smart-receipt-tracker" class="project-link">Try Live App</a>
            </div>
            
            <div class="project-card">
                <h3>Blog Summarizer</h3>
                <p>Transform lengthy articles into concise, actionable summaries using Azure Cognitive Services. Perfect for content creators and researchers who need quick insights.</p>
                <a href="/blog-summarizer" class="project-link">Explore</a>
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
        
        <footer class="contact">
            <h3>Contact</h3>
            <div style="margin-top: 1rem;">
                <a href="https://clydejuan.me" target="_blank">Portfolio</a>
                <a href="https://linkedin.com/in/clydesu" target="_blank">LinkedIn</a>
                <a href="mailto:clydezjuan@gmail.com">Email</a>
                <a href="https://github.com/clydesu/azure-projects" target="_blank">GitHub</a>
            </div>
        </footer>
    </div>
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
            <a href="/" class="back-button">← Back to Portfolio</a>
            <h1>Smart Receipt Tracker</h1>
            <p>AI-Powered Receipt Processing with Azure Document Intelligence</p>
        </div>
        
        <div class="content">
            <div class="info-note">
                <strong>Live Azure Integration:</strong> This application uses real Azure Document Intelligence for professional OCR processing. Upload your receipts to see AI in action!
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
            results.style.display = 'block';
            resultContent.innerHTML = `
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <h4 style="color: #667eea; margin-bottom: 15px;">Receipt Analysis Results</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                            <strong style="color: #495057;">Merchant</strong><br>
                            <span style="font-size: 1.1rem;">${data.merchant_name || 'Not detected'}</span>
                        </div>
                        <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
                            <strong style="color: #495057;">Total</strong><br>
                            <span style="font-size: 1.1rem; font-weight: bold;">$${data.total || '0.00'}</span>
                        </div>
                        <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;">
                            <strong style="color: #495057;">Date</strong><br>
                            <span style="font-size: 1.1rem;">${data.date || 'Not detected'}</span>
                        </div>
                    </div>
                    ${data.items && data.items.length > 0 ? 
                        '<div style="margin-top: 20px;"><h5 style="color: #495057; margin-bottom: 10px;">Items:</h5>' + 
                        data.items.map(item => `<div style="background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px;">${item.description || 'Item'} - $${item.total_price || 'N/A'}</div>`).join('') + 
                        '</div>' : ''
                    }
                </div>
            `;
        }

        function displayBulkResults(data) {
            results.style.display = 'block';
            
            let totalAmount = 0;
            let successCount = 0;
            
            data.results.forEach(receipt => {
                if (receipt.success && receipt.total) {
                    const amount = parseFloat(receipt.total.replace('$$', '')) || 0;
                    totalAmount += amount;
                    successCount++;
                }
            });
            
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
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
            
>>>>>>> parent of ed5435f (added reset button)
=======
>>>>>>> parent of b02bac1 (Clean up project and remove unnecessary files)
=======
>>>>>>> parent of b02bac1 (Clean up project and remove unnecessary files)
            let html = `
                <div style="background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                    <h3>Total Amount: $${totalAmount.toFixed(2)}</h3>
                    <p>Successfully processed: ${successCount} out of ${data.results.length} receipts</p>
                </div>
            `;
            
            data.results.forEach((receipt, index) => {
                const statusColor = receipt.success ? '#28a745' : '#dc3545';
                const statusIcon = receipt.success ? 'Success' : 'Error';
                
                html += `
                    <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid ${statusColor}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="color: #495057; margin-bottom: 10px;">${statusIcon} - Receipt ${index + 1}: ${receipt.filename}</h5>
                        ${receipt.success ? `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                                <div><strong>Merchant:</strong> ${receipt.merchant_name || 'Not detected'}</div>
                                <div><strong>Total:</strong> $${receipt.total || '0.00'}</div>
                                <div><strong>Date:</strong> ${receipt.date || 'Not detected'}</div>
                            </div>
                        ` : `
                            <p style="color: #dc3545;"><strong>Error:</strong> ${receipt.error}</p>
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

            let csvContent = "Filename,Merchant,Total,Date,Success,Error\\n";
            
            bulkProcessingResults.results.forEach(receipt => {
                const merchant = (receipt.merchant_name || 'N/A').replace(/"/g, '""');
                const total = receipt.total || '0.00';
                const date = receipt.date || 'N/A';
                const success = receipt.success ? 'Yes' : 'No';
                const error = receipt.error ? receipt.error.replace(/"/g, '""') : '';
                
                csvContent += `"$${receipt.filename}","$${merchant}","$${total}","$${date}","$${success}","$${error}"\\n`;
            });

            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `receipt_results_$${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
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
        image_data = file.read()
        result = process_receipt_image(image_data, file.filename)
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
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
        
        result = process_multiple_receipts(images_data)
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Error processing multiple receipts: {e}")
        response = jsonify({"error": "An unexpected error occurred"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/blog-summarizer')
def blog_summarizer():
    return send_from_directory('blog-summarizer', 'README.md')

@app.route('/meeting-analyst')
def meeting_analyst():
    return send_from_directory('meeting-analyst', 'README.md')

@app.route('/serverless-chatbot')
def serverless_chatbot():
    return send_from_directory('serverless-chatbot', 'README.md')

@app.route('/image-captioning-app')
def image_captioning_app():
    return send_from_directory('image-captioning-app', 'README.md')

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))