from flask import Flask, render_template, request, jsonify, send_from_directory
import re
import datetime
import math
import json
import random
from typing import Dict, Any, List
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.output: List[str] = []
        self.classes: Dict[str, Dict] = {}
        self.functions: Dict[str, callable] = {}
        
        # Initialize built-in functions
        self._init_builtins()

        # Update command patterns to handle articles
        self.command_patterns = {
            'create_var': [
                r'(?:Make|Create|Set|Let|Define|Initialize|Start|Begin with) (?:a |an |the )?(?:new )?(?:number|string|list|dict|set|variable)? ?(?:called |named |as )?(\w+) (?:equal to|to|be|as|with value) (.*)',
                r'I want (?:a |an |the )?(\w+) to be (.*)',
                r'Let\'s make (?:a |an |the )?(\w+) equal to (.*)',
                r'Give (?:me |us )?(?:a |an |the )?(\w+) (?:equal to|with|of) (.*)',
            ],
            'print': [
                r'(?:Print|Show|Display|Output|Tell me|What is|Log)(?: the| a| an)? (?:value of )?(?:variable )?([^,]+)',
                r'What(?:\'s| is)(?: the| a| an)? (?:value of )?([^,]+)',
                r'Show me(?: the| a| an)? ([^,]+)',
            ],
            'math_ops': [
                r'(?:Add|Plus|Increase|Increment|Put|Sum) (.*?) (?:to|into|in|with)(?: the| a| an)? (\w+)',
                r'Make(?: the| a| an)? (\w+) bigger by (.*)',
                r'Increase(?: the| a| an)? (\w+) by (.*)',
                r'(?:Subtract|Minus|Decrease|Take|Remove) (.*?) (?:from|out of)(?: the| a| an)? (\w+)',
                r'Make(?: the| a| an)? (\w+) smaller by (.*)',
                r'Decrease(?: the| a| an)? (\w+) by (.*)',
                r'(?:Multiply|Times)(?: the| a| an)? (\w+) by (.*)',
                r'Make(?: the| a| an)? (\w+) (.*) times bigger',
                r'Double(?: the| a| an)? (\w+)',
                r'(?:Divide|Split)(?: the| a| an)? (\w+) by (.*)',
                r'Make(?: the| a| an)? (\w+) (.*) times smaller',
                r'Half(?: the| a| an)? (\w+)',
            ],
            'conditional': [
                r'If(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
                r'When(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
                r'Check if(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
                r'Whenever(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
            ],
            'list_ops': [
                r'(?:Add|Append|Push) (.*?) (?:to|into|in)(?: the| a| an)? (\w+)(?: list)?',
                r'(?:Remove|Delete|Take) (.*?) (?:from|out of)(?: the| a| an)? (\w+)(?: list)?',
                r'Insert (.*?) (?:at|in) position (\d+) (?:of|in|to)(?: the| a| an)? (\w+)(?: list)?',
            ],
            'loop': [
                r'For each (?:item |element )?(?:in|of|from)(?: the| a| an)? (.*?):',
                r'While(?: the| a| an)? (.*?):',
                r'Repeat while(?: the| a| an)? (.*?):',
                r'Keep going (?:as long as|while)(?: the| a| an)? (.*?):',
            ],
        }

    def _init_builtins(self):
        """Initialize built-in functions and modules"""
        self.safe_builtins = {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'range': range,
            'round': round,
            'abs': abs,
            'sum': sum,
            'min': min,
            'max': max,
            'sorted': sorted,
            'random': random.random,
            'randint': random.randint,
            'math': {
                'pi': math.pi,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
            },
            'datetime': datetime.datetime.now,
        }

    def process_code(self, code: str) -> str:
        self.output = []
        try:
            # Process each line
            lines = code.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    # Handle indented blocks after conditionals
                    if line.endswith(':'):
                        block_lines = [line]
                        current_indent = self._get_indent(lines[i])
                        i += 1
                        while i < len(lines) and (
                            not lines[i].strip() or 
                            self._get_indent(lines[i]) > current_indent
                        ):
                            block_lines.append(lines[i])
                            i += 1
                        i -= 1  # Adjust for the outer loop increment
                        self.process_block(block_lines)
                    else:
                        self.process_line(line)
                i += 1
            
            return '\n'.join(self.output)
        except Exception as e:
            logger.error(f"Error processing code: {str(e)}")
            return f"Error: {str(e)}"

    def process_block(self, lines: List[str]):
        """Process a block of code (conditionals, loops, etc.)"""
        first_line = lines[0].strip()
        
        # Handle If statements
        if first_line.startswith('If'):
            condition = first_line[2:-1].strip()  # Remove 'If' and ':'
            indented_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            try:
                condition = self.translate_condition(condition)
                if eval(condition, {"__builtins__": self.safe_builtins}, self.variables):
                    for line in indented_lines:
                        self.process_line(line)
            except Exception as e:
                self.output.append(f"Error in conditional: {str(e)}")

    def process_line(self, line: str):
        """Process a single line with better article handling"""
        try:
            # Normalize the line and handle articles
            line = ' '.join(line.split())
            
            # Try each pattern category
            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if match := re.match(pattern, line, re.IGNORECASE):
                        if category == 'create_var':
                            name, value = match.groups()
                            # Clean variable name
                            name = self._clean_variable_name(name)
                            return self.create_variable(name, value)
                        elif category == 'print':
                            to_print = match.group(1)
                            # Clean print value
                            to_print = self._clean_variable_name(to_print)
                            return self.print_value(to_print)
                        elif category == 'math_ops':
                            amount, var_name = match.groups()
                            # Clean variable name
                            var_name = self._clean_variable_name(var_name)
                            return self.math_operation('Add', amount, var_name)
                        elif category == 'conditional':
                            condition, action, else_action = match.groups()
                            # Clean condition and actions
                            condition = self._clean_condition(condition)
                            action = action.strip()
                            if else_action:
                                else_action = else_action.strip()
                            return self.process_conditional(condition, action, else_action)

            self.output.append(f"I don't understand: {line}")

        except Exception as e:
            self.output.append(f"Error: {str(e)}")

    def process_conditional(self, condition: str, action: str, else_action: str = None):
        """Handle conditional statements with better article handling"""
        try:
            condition = self.translate_condition(condition)
            if eval(condition, {"__builtins__": self.safe_builtins}, self.variables):
                self.process_line(action)
            elif else_action:
                self.process_line(else_action)
        except Exception as e:
            self.output.append(f"Error in conditional: {str(e)}")

    def create_variable(self, name: str, value: str):
        """Handle variable creation with better error messages"""
        try:
            evaluated_value = eval(value, {"__builtins__": self.safe_builtins}, self.variables)
            self.variables[name] = evaluated_value
            self.output.append(f"Created {name} = {evaluated_value}")
        except Exception as e:
            self.output.append(f"I couldn't create {name}. {str(e)}")

    def print_value(self, to_print: str):
        """Handle printing values with better string handling"""
        to_print = to_print.strip()
        try:
            if (to_print.startswith('"') and to_print.endswith('"')) or \
               (to_print.startswith("'") and to_print.endswith("'")):
                self.output.append(to_print[1:-1])
            else:
                result = eval(to_print, {"__builtins__": self.safe_builtins}, self.variables)
                self.output.append(str(result))
        except Exception as e:
            self.output.append(f"I couldn't show {to_print}. {str(e)}")

    def math_operation(self, operation: str, amount: str, var_name: str):
        """Handle math operations with better error handling"""
        if var_name not in self.variables:
            self.output.append(f"I can't find a variable called {var_name}")
            return

        try:
            amount_val = eval(amount, {"__builtins__": self.safe_builtins}, self.variables)
            original = self.variables[var_name]

            if operation == 'Add':
                self.variables[var_name] += amount_val
                self.output.append(f"Added {amount_val} to {var_name} ({original} + {amount_val} = {self.variables[var_name]})")
            # ... (similar for other operations)

        except Exception as e:
            self.output.append(f"I couldn't {operation.lower()} {amount} to {var_name}. {str(e)}")

    def translate_condition(self, condition: str) -> str:
        """Translate natural language conditions to Python"""
        translations = {
            'is bigger than': '>',
            'is greater than': '>',
            'is less than': '<',
            'equals': '==',
            'is equal to': '==',
            'is not equal to': '!=',
            'is greater than or equal to': '>=',
            'is less than or equal to': '<=',
            'and': 'and',
            'or': 'or',
            'not': 'not',
            'contains': 'in',
            'is in': 'in',
            'is': '=='
        }
        
        # Process the condition
        for phrase, operator in translations.items():
            condition = condition.replace(phrase, operator)
        
        return condition

    def _get_indent(self, line: str) -> int:
        """Get the indentation level of a line"""
        return len(line) - len(line.lstrip())

    def _clean_variable_name(self, name: str) -> str:
        """Clean variable names by removing articles and extra spaces"""
        name = name.strip()
        for article in ['the ', 'a ', 'an ']:
            name = name.replace(article, '')
        return name

    def _clean_condition(self, condition: str) -> str:
        """Clean conditions by handling articles and normalizing spaces"""
        condition = condition.strip()
        # Handle articles in conditions
        condition = re.sub(r'\bthe\s+', '', condition)
        condition = re.sub(r'\ba\s+', '', condition)
        condition = re.sub(r'\ban\s+', '', condition)
        return condition

# Create Flask app
app = Flask(__name__)
interpreter = AdvancedInterpreter()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_code', methods=['POST'])
def run_code():
    try:
        code = request.json.get('code', '')
        if not code.strip():
            return jsonify({'output': 'Please write some code first!'})
            
        output = interpreter.process_code(code)
        return jsonify({'output': output})
    except Exception as e:
        logger.error(f"Error running code: {str(e)}")
        return jsonify({'error': f"Error: {str(e)}"}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                             'favicon.png', mimetype='image/png')

@app.route('/site.webmanifest')
def manifest():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'site.webmanifest', mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)