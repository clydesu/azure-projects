# app.py

from flask import Flask, render_template, request, jsonify
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/smart-receipt-tracker")
def smart_receipt_tracker():
    return render_template("../smart-receipt-tracker/templates/receipt_tracker.html")

@app.route("/upload-receipt", methods=["POST"])
def upload_receipt():
    if 'receipt' not in request.files:
        return jsonify({"error": "No receipt file provided"}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Call Azure Function to process the receipt
    try:
        function_url = os.getenv('AZURE_FUNCTION_URL', 'https://your-function-app.azurewebsites.net')
        
        files = {'receipt': (file.filename, file.read(), file.content_type)}
        response = requests.post(f"{function_url}/api/process_receipt", files=files)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({"error": "Failed to process receipt"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/blog-summarizer")
def blog_summarizer():
    return "<h1>Blog Summarizer</h1><p>Coming soon - Azure OpenAI integration for automatic blog content summarization</p>"

@app.route("/meeting-analyst")
def meeting_analyst():
    return "<h1>Meeting Analyst</h1><p>Coming soon - Azure Speech-to-Text & OpenAI integration for meeting transcription and analysis</p>"

@app.route("/serverless-chatbot")
def serverless_chatbot():
    return "<h1>Serverless Chatbot</h1><p>Coming soon - Azure Functions & OpenAI integration for scalable conversational AI</p>"

@app.route("/image-captioning-app")
def image_captioning():
    return "<h1>Image Captioning App</h1><p>Coming soon - Azure Computer Vision integration for automatic image description generation</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
