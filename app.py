import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Import the existing brain process
from brain import process_command

app = Flask(__name__)
load_dotenv()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint that receives text from the web frontend and returns the AI's response."""
    data = request.json
    user_text = data.get("text", "")
    
    if not user_text:
        return jsonify({"response": "I didn't hear anything."})
    
    try:
        # Pass the transcribed text to our existing LLM Brain
        response_text = process_command(user_text)
        return jsonify({"response": response_text})
    except Exception as e:
        print(f"Error handling chat: {e}")
        return jsonify({"response": "Sorry, I encountered an internal error."})

if __name__ == '__main__':
    # Run the server on localhost
    print("Starting Web Interface on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
