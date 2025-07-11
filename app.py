# app.py

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/resume-screener")
def resume_screener():
    return "<h1>Resume Screener Bot</h1><p>Coming soon - Azure AI Document Intelligence & OpenAI integration for intelligent resume analysis</p>"

@app.route("/blog-summarizer")
def blog_summarizer():
    return "<h1>Blog Summarizer</h1><p>Coming soon - Azure OpenAI integration for automatic blog content summarization</p>"

@app.route("/meeting-analyst")
def meeting_analyst():
    return "<h1>Meeting Analyst</h1><p>Coming soon - Azure Speech-to-Text & OpenAI integration for meeting transcription and analysis</p>"

@app.route("/serverless-chatbot")
def serverless_chatbot():
    return "<h1>Serverless Chatbot</h1><p>Coming soon - Azure Functions & OpenAI integration for scalable conversational AI</p>"

@app.route("/image-captioning")
def image_captioning():
    return "<h1>Image Captioning App</h1><p>Coming soon - Azure Computer Vision integration for automatic image description generation</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
