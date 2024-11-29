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

        # Update command patterns with more natural language support
        self.command_patterns = {
            'create_var': [
                # Basic variable creation with more natural language
                r'(?:Make|Create|Set|Let|Define|Give me) (?:a |an |the )?(?:new )?(?:number|string|list|dict|set|variable)? ?(?:called |named |as )?(\w+) (?:equal to|to|be|as|with|with value|that is) (.*)',
                # More natural patterns with flexible syntax
                r'(?:Make|Create|Set|Let|Define|Give me) (?:a |an |the )?(?:new )?(\w+) (?:called |named |as )?(.*?) (?:equal to|to|be|as|with|with value|that is) (.*)',
                # Direct assignment pattern
                r'(?:Let|Set) (\w+) (?:be|equal|to) (.*)',
            ],
            'print': [
                # Basic printing with natural language
                r'(?:Print|Show|Display|Output|Tell me|What is)(?: the| a| an)? (?:value of )?(?:variable )?([^,]+)',
                # Special cases for string literals
                r'(?:Print|Show|Display|Output|Say) ["\'](.+)["\']',
                # Natural queries
                r'(?:What is|Tell me|Show me)(?: the)? (?:value of )?(.+)',
            ],
            'math_ops': [
                # Addition with natural language
                r'(?:Add|Plus|Increase|Put|Include) (.*?) (?:to|into|in|with)(?: the| a| an)? (\w+)',
                r'(?:Increase|Make bigger|Raise)(?: the| a| an)? (\w+) (?:by|with) (.*)',
                r'(?:Make|Let)(?: the| a| an)? (\w+) (?:bigger|larger|greater) (?:by|with) (.*)',
                # Subtraction with natural language
                r'(?:Subtract|Minus|Decrease|Take|Remove|Reduce) (.*?) (?:from|out of)(?: the| a| an)? (\w+)',
                r'(?:Decrease|Make smaller|Lower)(?: the| a| an)? (\w+) (?:by|with) (.*)',
                # Multiplication with natural language
                r'(?:Multiply|Times|Scale)(?: the| a| an)? (\w+) (?:by|with) (.*)',
                r'(?:Double|Triple|Quadruple)(?: the| a| an)? (\w+)',
                # Division with natural language
                r'(?:Divide|Split|Share)(?: the| a| an)? (\w+) (?:by|into|in) (.*)',
                r'(?:Half|Quarter)(?: the| a| an)? (\w+)',
            ],
            'list_ops': [
                # List operations with natural language
                r'(?:Add|Put|Place|Insert) (.*?) (?:to|into|in|at the end of)(?: the| a| an)? (\w+)',
                r'(?:Remove|Delete|Take out) (.*?) (?:from|out of)(?: the| a| an)? (\w+)',
                r'(?:Insert|Put|Place) (.*?) (?:at|in) (?:position |index |spot )?(\d+) (?:in|of|at)(?: the| a| an)? (\w+)',
            ],
            'math_funcs': [
                # Math functions with natural language
                r'(?:Calculate|Compute|Find|Get|What is|Tell me)(?: the)? (?:square root|sqrt) of (.*)',
                r'(?:Show|Display|Print|Get|What is|Tell me)(?: the)? (?:value of )?pi',
                r'(?:Generate|Create|Give me|Get|Make)(?: a)? random number',
                r'(?:Find|Get|Calculate|What is)(?: the)? (?:maximum|max|highest|biggest) (?:value )?(?:of|in|from) (.*)',
            ],
        }

    def _init_builtins(self):
        """Initialize built-in functions and modules with extended math support"""
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
                'floor': math.floor,
                'ceil': math.ceil,
                'exp': math.exp,
                'log': math.log,
                'pow': math.pow,
            },
            'datetime': datetime.datetime.now,
        }

    def process_line(self, line: str):
        """Process a single line with improved natural language handling"""
        try:
            # Normalize the line
            line = ' '.join(line.split())
            
            # Try each pattern category
            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if match := re.match(pattern, line, re.IGNORECASE):
                        if category == 'create_var':
                            # Handle variable creation
                            if len(match.groups()) == 3:  # Extended pattern
                                _, name, value = match.groups()
                            else:  # Basic pattern
                                name, value = match.groups()
                            name = self._clean_variable_name(name)
                            return self.create_variable(name, value)
                            
                        elif category == 'print':
                            # Handle printing
                            to_print = match.group(1)
                            return self.print_value(to_print)
                            
                        elif category == 'math_ops':
                            # Handle math operations
                            if 'Make' in pattern or 'Increase' in pattern:
                                var_name = match.group(1)
                                amount = match.group(2)
                            else:
                                amount, var_name = match.groups()
                            var_name = self._clean_variable_name(var_name)
                            operation = self._determine_math_operation(pattern)
                            if operation:
                                return self.math_operation(operation, amount, var_name)

            # If no pattern matched, try to understand as a natural expression
            self.output.append(f"I don't understand: {line}")

        except Exception as e:
            self.output.append(f"Error: {str(e)}")

    def _determine_math_operation(self, pattern: str) -> str:
        """Determine the math operation from the pattern"""
        operations = {
            'Add': ['add', 'plus', 'increase', 'increment'],
            'Subtract': ['subtract', 'minus', 'decrease', 'decrement'],
            'Multiply': ['multiply', 'times', 'scale'],
            'Divide': ['divide', 'split'],
            'Double': ['double'],
            'Half': ['half'],
            'Increase': ['increase', 'make bigger'],
            'Decrease': ['decrease', 'make smaller']
        }
        
        pattern_lower = pattern.lower()
        for op, keywords in operations.items():
            if any(keyword in pattern_lower for keyword in keywords):
                return op
        return None

    def math_operation(self, operation: str, amount: str, var_name: str):
        """Handle math operations with improved value handling"""
        try:
            if var_name not in self.variables:
                self.output.append(f"I can't find a variable called {var_name}")
                return

            original = self.variables[var_name]
            
            # Process the amount with better numeric handling
            try:
                # Handle numeric literals first
                if str(amount).replace('.', '', 1).isdigit():
                    amount_val = float(amount)
                # Then handle variable references
                elif amount in self.variables:
                    amount_val = float(self.variables[amount])
                # Finally try evaluation with stripped quotes
                else:
                    clean_amount = amount.strip('"\'')
                    amount_val = float(clean_amount)

                # Perform the operation with improved error handling
                operations = {
                    'Add': lambda x, y: x + y,
                    'Subtract': lambda x, y: x - y,
                    'Multiply': lambda x, y: x * y,
                    'Divide': lambda x, y: x / y if y != 0 else None,
                    'Double': lambda x, _: x * 2,
                    'Half': lambda x, _: x / 2,
                    'Increase': lambda x, y: x + y,
                    'Decrease': lambda x, y: x - y
                }

                if operation in operations:
                    result = operations[operation](float(original), amount_val)
                    if result is not None:
                        self.variables[var_name] = result
                        self.output.append(f"Updated {var_name} from {original} to {result}")
                    else:
                        self.output.append(f"Cannot divide by zero")
                else:
                    self.output.append(f"Unknown operation: {operation}")

            except ValueError:
                self.output.append(f"Cannot convert {amount} to a number")
            except Exception as e:
                self.output.append(f"Error in math operation: {str(e)}")

        except Exception as e:
            self.output.append(f"Error in math operation: {str(e)}")

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