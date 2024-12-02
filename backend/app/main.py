from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from .interpreter.interpreter import AdvancedInterpreter

app = Flask(__name__)
CORS(app)

@app.route('/api/run_code', methods=['POST'])
def run_code():
    try:
        code = request.json.get('code', '')
        if not code.strip():
            return jsonify({'output': 'Please write some code first!'})
            
        interpreter = AdvancedInterpreter()
        output = interpreter.process_code(code)
        return jsonify({'output': output})
    except Exception as e:
        logging.error(f"Error running code: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 