#############################
# app_openai.py
#############################

import os
import openai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Make sure your API key is set in an environment variable, e.g.:
# export OPENAI_API_KEY="sk-..."
# or in your Render / Heroku dashboard config.

openai.api_key = os.environ.get("OPENAI_API_KEY", "")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    # Serve your HTML/JS front end
    return render_template('index.html')

@app.route('/run_code', methods=['POST'])
def run_code():
    """
    Replaces local AdvancedInterpreter logic:
    1. We receive 'code' from the front end as user instructions or "NLP" text.
    2. We call OpenAI's ChatCompletion API with that text as the prompt.
    3. Return AI's response.
    """
    try:
        user_instructions = request.json.get('code', '').strip()
        if not user_instructions:
            return jsonify({'output': 'Please write some instructions first!'})

        # Prepare messages for ChatCompletion
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI that interprets natural language instructions and returns a result. "
                    "Respond with the result of interpreting or 'executing' the user's instructions. "
                    "Only return the output, do not include extra explanations."
                )
            },
            {
                "role": "user",
                "content": user_instructions
            }
        ]

        # Call OpenAI ChatCompletion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=messages,
            temperature=0
        )
        
        # Extract the assistant's reply
        ai_reply = response.choices[0].message.content if response.choices else ""

        return jsonify({'output': ai_reply})
    
    except Exception as e:
        return jsonify({'error': f"Error calling OpenAI: {str(e)}"}), 500

@app.route('/input', methods=['POST'])
def handle_input():
    """
    If you still need a separate /input endpoint, you can do something similar here:
    forward user input to OpenAI with a different prompt or context, etc.
    """
    try:
        user_input = request.json.get('input', '').strip()
        if not user_input:
            return jsonify({'error': 'No input provided'})
        
        # Possibly do another ChatCompletion call here
        # For now, we’ll just echo it or return an empty logic placeholder:
        return jsonify({'output': "No separate logic implemented for /input right now."})
    
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)