from flask import Flask, render_template, request, jsonify
import re

class NaturalPythonInterpreter:
    def __init__(self):
        self.variables = {}
        self.output = []

    def process_code(self, natural_code):
        self.output = []
        self.variables.clear()
        
        for line in natural_code.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                self.process_line(line.strip())
                
        return '\n'.join(self.output)

    def process_line(self, line):
        try:
            # Make/Create variable
            if match := re.match(r'Make (?:a )?(?:number )?called (\w+) equal to (.*)', line):
                name, value = match.groups()
                try:
                    self.variables[name] = eval(value, {"__builtins__": {}}, self.variables)
                    self.output.append(f"Created {name} with value {self.variables[name]}")
                except:
                    self.output.append(f"I couldn't understand the value for {name}")
            
            # Print/Show value
            elif line.startswith(('Print', 'Show', 'Display')):
                var_name = line.split()[-1]
                if var_name in self.variables:
                    self.output.append(f"{var_name} = {self.variables[var_name]}")
                else:
                    self.output.append(f"I don't know what {var_name} is yet")
            
            # Add to variable
            elif match := re.match(r'Add (\d+) to (\w+)', line):
                amount, var_name = match.groups()
                if var_name in self.variables:
                    self.variables[var_name] += int(amount)
                    self.output.append(f"Added {amount} to {var_name}. New value: {self.variables[var_name]}")
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
                        self.output.append(f"I had trouble understanding that condition")
            
            else:
                self.output.append(f"I'm not sure what you mean by: {line}")
                
        except Exception as e:
            self.output.append(f"Oops! Something went wrong: {str(e)}")

    def translate_condition(self, condition):
        condition = condition.replace('is bigger than', '>')
        condition = condition.replace('is less than', '<')
        condition = condition.replace('equals', '==')
        condition = condition.replace('is equal to', '==')
        return condition

app = Flask(__name__)
interpreter = NaturalPythonInterpreter()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    output = interpreter.process_code(code)
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)