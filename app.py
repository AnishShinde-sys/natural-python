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
                # Basic variable creation
                r'(?:Make|Create|Set|Let|Define) (?:a |an |the )?(?:new )?(?:number|string|list|dict|set|variable)? ?(?:called |named |as )?(\w+) (?:equal to|to|be|as|with|with value) (.*)',
                # More natural patterns
                r'(?:Make|Create|Set|Let|Define) (?:a |an |the )?(?:new )?(\w+) (?:called |named |as )?(.*?) (?:equal to|to|be|as|with|with value) (.*)',
            ],
            'print': [
                # Basic printing
                r'(?:Print|Show|Display|Output|Tell me about|What is)(?: the| a| an)? (?:value of )?(?:variable )?([^,]+)',
                # Special cases
                r'(?:Print|Show|Display|Output) ["\'](.+)["\']',
            ],
            'math_ops': [
                # Addition
                r'(?:Add|Plus|Increase|Increment) (.*?) (?:to|into|in|with)(?: the| a| an)? (\w+)',
                # Subtraction
                r'(?:Subtract|Minus|Decrease|Take|Remove) (.*?) (?:from|out of)(?: the| a| an)? (\w+)',
                # Multiplication
                r'(?:Multiply|Times)(?: the| a| an)? (\w+) by (.*)',
                # Division
                r'(?:Divide|Split)(?: the| a| an)? (\w+) by (.*)',
            ],
            'list_ops': [
                # List creation
                r'(?:Make|Create|Define) (?:a |an |the )?list (?:called |named |as )?(\w+) (?:equal to |to |with |containing )?(\[.+\])',
                # Add to list
                r'(?:Add|Append|Push) (.*?) (?:to|into|in)(?: the| a| an)? (\w+)',
                # Remove from list
                r'(?:Remove|Delete|Take) (.*?) (?:from|out of)(?: the| a| an)? (\w+)',
                # Insert at position
                r'Insert (.*?) (?:at|in) position (\d+) (?:in|of|at)(?: the| a| an)? (\w+)',
            ],
            'math_funcs': [
                r'(?:Calculate |Compute |Find |Get |What is )?(?:the )?(?:square root|sqrt) of (.*)',
                r'(?:Show|Display|Print|Get|What is)(?: the)? (?:value of )?pi',
                r'(?:Generate|Create|Give me|Get)(?: a)? random number',
                r'(?:Find|Get|Calculate|What is)(?: the)? (?:maximum|max|highest) (?:of|in|from) (.*)',
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
        
        # Handle If statements with better article handling
        if first_line.startswith('If'):
            # Extract condition and remove 'If' and ':'
            condition = first_line[2:-1].strip() if first_line.endswith(':') else first_line[2:].strip()
            indented_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            try:
                # Clean and translate the condition
                condition = self._clean_condition(condition)
                condition = self.translate_condition(condition)
                
                if eval(condition, {"__builtins__": self.safe_builtins}, self.variables):
                    for line in indented_lines:
                        self.process_line(line)
            except Exception as e:
                self.output.append(f"Error in if statement: {str(e)}")

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
                            if len(match.groups()) == 3:  # Extended pattern
                                _, name, value = match.groups()
                            else:  # Basic pattern
                                name, value = match.groups()
                            name = self._clean_variable_name(name)
                            return self.create_variable(name, value)
                        elif category == 'print':
                            to_print = match.group(1)
                            return self.print_value(to_print)
                        elif category == 'math_ops':
                            if 'Add' in pattern or 'Plus' in pattern:
                                amount, var_name = match.groups()
                                var_name = self._clean_variable_name(var_name)
                                return self.math_operation('Add', amount, var_name)
                            # ... (similar for other operations)
                        elif category == 'math_funcs':
                            if 'square root' in pattern or 'sqrt' in pattern:
                                num = match.group(1)
                                return self.math_function('sqrt', num)
                            elif 'pi' in pattern:
                                return self.math_function('pi')
                            elif 'random' in pattern:
                                return self.math_function('random')
                            elif 'maximum' in pattern or 'max' in pattern:
                                values = match.group(1)
                                return self.math_function('max', values)

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
        """Translate natural language conditions to Python with better article handling"""
        # First clean any articles
        condition = self._clean_condition(condition)
        
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
        
        # Clean up any extra spaces around operators
        condition = re.sub(r'\s+([><=!]+)\s+', r'\1', condition)
        
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
        
        # Handle articles with word boundaries
        condition = re.sub(r'\bthe\s+', '', condition)
        condition = re.sub(r'\ba\s+', '', condition)
        condition = re.sub(r'\ban\s+', '', condition)
        
        # Normalize spaces
        condition = ' '.join(condition.split())
        
        return condition

    def math_function(self, func: str, *args):
        """Handle math functions"""
        try:
            if func == 'sqrt':
                num = eval(args[0], {"__builtins__": self.safe_builtins}, self.variables)
                result = math.sqrt(num)
                self.output.append(str(result))
            elif func == 'pi':
                self.output.append(str(math.pi))
            elif func == 'random':
                self.output.append(str(random.random()))
            elif func == 'max':
                values = eval(args[0], {"__builtins__": self.safe_builtins}, self.variables)
                result = max(values)
                self.output.append(str(result))
        except Exception as e:
            self.output.append(f"Error in math function {func}: {str(e)}")

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