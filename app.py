from flask import Flask, send_from_directory, render_template_string
import os

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
        </header>
        
        <div class="projects-grid">
            <div class="project-card">
                <h3>🧾 Smart Receipt Tracker</h3>
                <p>Receipt processing application using Azure Document Intelligence to extract merchant information, amounts, and dates from receipt images.</p>
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
            <a href="https://azure-portfolio-projects.azurewebsites.net" class="demo-link" target="_blank">Try Smart Receipt Tracker</a>
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
