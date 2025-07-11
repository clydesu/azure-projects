# app.py

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sentiment-analysis")
def sentiment():
    return "<h1>Sentiment Analysis</h1><p>Coming soon - Azure Text Analytics integration</p>"

@app.route("/chatbot")
def chatbot():
    return "<h1>AI Chatbot</h1><p>Coming soon - Azure OpenAI integration</p>"

@app.route("/tts")
def tts():
    return "<h1>Text-to-Speech</h1><p>Coming soon - Azure Speech Services integration</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
