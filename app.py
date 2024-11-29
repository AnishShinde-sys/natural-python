from flask import Flask, render_template, request, jsonify
import re
import datetime
import math
import json
import random
from typing import Dict, Any, List
import logging

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
            ],
            'print': [
                r'(?:Print|Show|Display|Output|Tell me|What is|Log)(?: the| a| an)? (?:value of )?(?:variable )?([^,]+)',
                r'What(?:\'s| is)(?: the| a| an)? (?:value of )?([^,]+)',
            ],
            'math_ops': [
                # Addition
                r'(?:Add|Plus|Increase|Increment|Put|Sum) (.*?) (?:to|into|in|with)(?: the| a| an)? (\w+)',
                r'Make(?: the| a| an)? (\w+) bigger by (.*)',
                # Subtraction
                r'(?:Subtract|Minus|Decrease|Take|Remove) (.*?) (?:from|out of)(?: the| a| an)? (\w+)',
                r'Make(?: the| a| an)? (\w+) smaller by (.*)',
                # Multiplication
                r'(?:Multiply|Times)(?: the| a| an)? (\w+) by (.*)',
                r'Make(?: the| a| an)? (\w+) (.*) times bigger',
                # Division
                r'(?:Divide|Split)(?: the| a| an)? (\w+) by (.*)',
                r'Make(?: the| a| an)? (\w+) (.*) times smaller',
            ],
            'conditional': [
                r'If(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
                r'When(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
                r'Check if(?: the| a| an)? (.*?), (.*?)(?:\s+(?:else|otherwise|if not)\s+(.*))?$',
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
                    # Handle multiline constructs
                    if any(line.startswith(keyword) for keyword in ['Create class', 'Define function', 'For each', 'While']):
                        block_lines = [line]
                        indent = self._get_indent(lines[i+1]) if i+1 < len(lines) else 0
                        i += 1
                        while i < len(lines) and (not lines[i].strip() or self._get_indent(lines[i]) > indent):
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
        """Process a block of code (class, function, loop, etc.)"""
        first_line = lines[0].strip()
        
        # Class definition
        if first_line.startswith('Create class'):
            match = re.match(r'Create class (\w+)(?:\s+extends\s+(\w+))?', first_line)
            if match:
                class_name, parent_class = match.groups()
                self.create_class(class_name, parent_class, lines[1:])
        
        # Function definition
        elif first_line.startswith('Define function'):
            match = re.match(r'Define function (\w+)\s*\((.*?)\)', first_line)
            if match:
                func_name, params = match.groups()
                self.create_function(func_name, params, lines[1:])
        
        # For loop
        elif first_line.startswith('For each'):
            match = re.match(r'For each (\w+) in (.*?):', first_line)
            if match:
                var_name, iterable = match.groups()
                self.process_for_loop(var_name, iterable, lines[1:])
        
        # While loop
        elif first_line.startswith('While'):
            match = re.match(r'While (.*?):', first_line)
            if match:
                condition = match.group(1)
                self.process_while_loop(condition, lines[1:])

    def process_line(self, line: str):
        """Process a single line of natural language code"""
        try:
            # Remove extra spaces and normalize the line
            line = ' '.join(line.split())
            
            # Try each pattern category
            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if match := re.match(pattern, line, re.IGNORECASE):
                        if category == 'create_var':
                            name, value = match.groups()
                            # Remove any articles from the variable name
                            name = name.strip().replace('the ', '').replace('a ', '').replace('an ', '')
                            return self.create_variable(name, value)
                        elif category == 'print':
                            to_print = match.group(1)
                            # Remove any articles from what we're printing
                            to_print = to_print.strip().replace('the ', '').replace('a ', '').replace('an ', '')
                            return self.print_value(to_print)
                        elif category == 'math_ops':
                            if 'Add' in pattern or 'Plus' in pattern or 'Increase' in pattern:
                                amount, var_name = match.groups()
                                # Remove any articles from the variable name
                                var_name = var_name.strip().replace('the ', '').replace('a ', '').replace('an ', '')
                                return self.math_operation('Add', amount, var_name)
                            # ... (similar for other operations)
                        elif category == 'conditional':
                            condition, action, else_action = match.groups()
                            # Clean up the condition and actions
                            condition = condition.strip()
                            action = action.strip()
                            if else_action:
                                else_action = else_action.strip()
                            return self.process_conditional(condition, action, else_action)

            # If no pattern matches
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

if __name__ == '__main__':
    app.run(debug=True)