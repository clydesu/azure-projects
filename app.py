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
    DOCUMENT_INTELLIGENCE_AVAILABLE = True
    logger.info("Document Intelligence service imported successfully")
except ImportError as e:
    DOCUMENT_INTELLIGENCE_AVAILABLE = False
    logger.warning(f"Document Intelligence service not available: {e}")

# Document Intelligence endpoints with real Azure integration
@app.route('/api/process_receipt', methods=['POST', 'OPTIONS'])
def process_receipt():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    if not DOCUMENT_INTELLIGENCE_AVAILABLE:
        response = jsonify({"error": "Document Intelligence service not available"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 503
    
    try:
        # Get image data from request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({"error": "Unsupported file type. Please use JPG, PNG, BMP, TIFF, or PDF"}), 400
        
        # Read file data
        image_data = file.read()
        
        # Validate file size (max 50MB for Document Intelligence)
        if len(image_data) > 50 * 1024 * 1024:
            return jsonify({"error": "File too large. Maximum size is 50MB"}), 400
        
        logger.info(f"Processing receipt upload: {file.filename}, size: {len(image_data)} bytes")
        
        # Process with Document Intelligence
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
    
    if not DOCUMENT_INTELLIGENCE_AVAILABLE:
        response = jsonify({"error": "Document Intelligence service not available"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 503
    
    try:
        # Get multiple files from request
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "No files selected"}), 400
        
        # Validate file count (limit to 10 files)
        if len(files) > 10:
            return jsonify({"error": "Maximum 10 files allowed per request"}), 400
        
        # Prepare images data for processing
        images_data = []
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf'}
        
        for file in files:
            if file.filename == '':
                continue
                
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                images_data.append({
                    'filename': file.filename,
                    'error': f"Unsupported file type: {file_ext}"
                })
                continue
            
            image_data = file.read()
            if len(image_data) > 50 * 1024 * 1024:
                images_data.append({
                    'filename': file.filename,
                    'error': "File too large (max 50MB)"
                })
                continue
            
            images_data.append({
                'filename': file.filename,
                'data': image_data
            })
        
        logger.info(f"Processing {len(images_data)} receipt uploads")
        
        # Process with Document Intelligence
        result = process_multiple_receipts(images_data)
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Error processing multiple receipts: {e}")
        response = jsonify({"error": "An unexpected error occurred"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

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
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .project-card {
            background: white;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .project-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .project-card h3 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .project-card p {
            margin-bottom: 1.5rem;
            color: #666;
        }
        
        .project-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.8rem 1.5rem;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }
        
        .project-link:hover {
            background: #5a6fd8;
        }
        
        .demo-section {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .demo-link {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 5px;
            font-size: 1.1rem;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s ease;
        }
        
        .demo-link:hover {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.6);
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
            <p>Showcasing AI-powered applications built with Azure Cognitive Services</p>
            <p><small>Deployed via GitHub Actions 🚀</small></p>
        </header>
        
        <div class="projects-grid">
            <div class="project-card">
                <h3>🧾 Smart Receipt Tracker</h3>
                <p>Professional receipt processing application powered by Azure Document Intelligence. Automatically extracts merchant information, amounts, dates, and itemized purchases from receipt images with high accuracy OCR technology.</p>
                <a href="/smart-receipt-tracker" class="project-link">View Project</a>
            </div>
            
            <div class="project-card">
                <h3>📝 Blog Summarizer</h3>
                <p>AI-powered content summarization tool that uses Azure Cognitive Services to create concise summaries of blog posts and articles.</p>
                <a href="/blog-summarizer" class="project-link">View Project</a>
            </div>
            
            <div class="project-card">
                <h3>🎙️ Meeting Analyst</h3>
                <p>Meeting transcription and analysis application that converts speech to text and provides insights using Azure Speech Services.</p>
                <a href="/meeting-analyst" class="project-link">View Project</a>
            </div>
            
            <div class="project-card">
                <h3>🤖 Serverless Chatbot</h3>
                <p>AI chatbot with natural language processing capabilities built using Azure Bot Framework and Language Understanding.</p>
                <a href="/serverless-chatbot" class="project-link">View Project</a>
            </div>
            
            <div class="project-card">
                <h3>📸 Image Captioning App</h3>
                <p>AI-powered image description generator that uses Azure Computer Vision to automatically generate captions for uploaded images.</p>
                <a href="/image-captioning-app" class="project-link">View Project</a>
            </div>
        </div>
        
        <div class="demo-section">
            <h2 style="color: white; margin-bottom: 1rem;">🚀 Live Demo</h2>
            <p style="color: white; margin-bottom: 1.5rem;">Experience the Smart Receipt Tracker in action</p>
            <a href="/smart-receipt-tracker" class="demo-link">Try Smart Receipt Tracker</a>
        </div>
        
        <footer class="contact">
            <h3>Contact</h3>
            <div style="margin-top: 1rem;">
                <a href="https://clydejuan.me" target="_blank">🌐 Portfolio</a>
                <a href="https://linkedin.com/in/clydesu" target="_blank">💼 LinkedIn</a>
                <a href="mailto:clydezjuan@gmail.com">📧 Email</a>
                <a href="https://github.com/clydesu/azure-projects" target="_blank">📁 GitHub</a>
            </div>
        </footer>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(portfolio_template)

@app.route('/smart-receipt-tracker')
def smart_receipt_tracker():
    return send_from_directory('smart-receipt-tracker', 'index.html')

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
