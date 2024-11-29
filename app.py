from flask import Flask, render_template, request, jsonify
import re
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleInterpreter:
    def __init__(self):
        self.variables = {}
        self.output = []

    def process_code(self, code: str) -> str:
        """Process natural language code into Python output"""
        self.output = []
        self.variables.clear()
        
        # Process each line
        for line in code.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                self.process_line(line.strip())
                
        return '\n'.join(self.output)

    def process_line(self, line: str) -> None:
        """Process a single line of natural language code"""
        try:
            # Make a variable
            if match := re.match(r'Make (?:a )?(?:number )?called (\w+) equal to (.*)', line):
                name, value = match.groups()
                try:
                    self.variables[name] = eval(value, {"__builtins__": {}}, self.variables)
                    self.output.append(f"Created {name} = {self.variables[name]}")
                except:
                    self.output.append(f"I couldn't understand the value for {name}")
            
            # Print a value
            elif line.startswith(('Print', 'Show', 'Display')):
                var_name = line.split()[-1].strip('"\'')
                if var_name in self.variables:
                    self.output.append(f"{var_name} = {self.variables[var_name]}")
                else:
                    self.output.append(f"I don't know what {var_name} is yet")
            
            # Add to a variable
            elif match := re.match(r'Add (\d+) to (\w+)', line):
                amount, var_name = match.groups()
                if var_name in self.variables:
                    self.variables[var_name] += int(amount)
                    self.output.append(f"Added {amount} to {var_name}. Now {var_name} = {self.variables[var_name]}")
                else:
                    self.output.append(f"I can't find a variable called {var_name}")
            
            # If statement
            elif line.startswith('If'):
                match = re.match(r'If (.*?), (.*)', line)
                if match:
                    condition, action = match.groups()
                    condition = self.translate_condition(condition)
                    try:
                        if eval(condition, {"__builtins__": {}}, self.variables):
                            self.process_line(action)
                    except:
                        self.output.append(f"I had trouble with that if statement")
            
            else:
                self.output.append(f"I'm not sure what you mean by: {line}")
                
        except Exception as e:
            self.output.append(f"Oops! Something went wrong: {str(e)}")

    def translate_condition(self, condition: str) -> str:
        """Translate natural language conditions to Python"""
        condition = condition.replace('is bigger than', '>')
        condition = condition.replace('is less than', '<')
        condition = condition.replace('equals', '==')
        condition = condition.replace('is equal to', '==')
        return condition

# Create Flask app
app = Flask(__name__)
interpreter = SimpleInterpreter()

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/run_code', methods=['POST'])
def run_code():
    """Run the code and return output"""
    try:
        code = request.json.get('code', '')
        if not code.strip():
            return jsonify({'output': 'Please write some code first!'})
            
        output = interpreter.process_code(code)
        return jsonify({'output': output})
    except Exception as e:
        logger.error(f"Error running code: {str(e)}")
        return jsonify({'error': 'Oops! Something went wrong. Try again!'}), 500

if __name__ == '__main__':
    app.run(debug=True)