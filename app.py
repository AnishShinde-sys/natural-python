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
            # Variable creation and assignment
            if match := re.match(r'(?:Make|Create|Set) (?:a )?(?:number|string|list|dict|set)? ?called (\w+) (?:equal to|to) (.*)', line):
                name, value = match.groups()
                try:
                    evaluated_value = eval(value, {"__builtins__": self.safe_builtins}, self.variables)
                    self.variables[name] = evaluated_value
                    self.output.append(f"Created {name} = {evaluated_value}")
                except Exception as e:
                    self.output.append(f"Couldn't create {name}: {str(e)}")

            # Print/Display with string handling
            elif line.startswith(('Print', 'Show', 'Display')):
                to_print = line.split(' ', 1)[1].strip()
                try:
                    # Check if it's a quoted string
                    if (to_print.startswith('"') and to_print.endswith('"')) or \
                       (to_print.startswith("'") and to_print.endswith("'")):
                        # Remove quotes and print directly
                        self.output.append(to_print[1:-1])
                    else:
                        # Evaluate as a variable or expression
                        result = eval(to_print, {"__builtins__": self.safe_builtins}, self.variables)
                        self.output.append(str(result))
                except Exception as e:
                    self.output.append(f"Couldn't display {to_print}: {str(e)}")

            # Math operations
            elif match := re.match(r'(Add|Subtract|Multiply|Divide) (.*?) (?:to|from|by) (\w+)', line):
                op, amount, var_name = match.groups()
                if var_name in self.variables:
                    try:
                        amount_val = eval(amount, {"__builtins__": self.safe_builtins}, self.variables)
                        if op == 'Add':
                            self.variables[var_name] += amount_val
                        elif op == 'Subtract':
                            self.variables[var_name] -= amount_val
                        elif op == 'Multiply':
                            self.variables[var_name] *= amount_val
                        elif op == 'Divide':
                            self.variables[var_name] /= amount_val
                        self.output.append(f"{op}ed {amount} to {var_name}. Result: {self.variables[var_name]}")
                    except Exception as e:
                        self.output.append(f"Couldn't perform {op.lower()} operation: {str(e)}")
                else:
                    self.output.append(f"Variable {var_name} not found")

            # List operations
            elif match := re.match(r'(Append|Remove|Insert) (.*?) (?:to|from|at) (\w+)(?: at (?:index|position) (\d+))?', line):
                op, item, list_name, pos = match.groups()
                if list_name in self.variables and isinstance(self.variables[list_name], list):
                    try:
                        if op == 'Append':
                            self.variables[list_name].append(eval(item, {"__builtins__": self.safe_builtins}, self.variables))
                        elif op == 'Remove':
                            self.variables[list_name].remove(eval(item, {"__builtins__": self.safe_builtins}, self.variables))
                        elif op == 'Insert' and pos:
                            self.variables[list_name].insert(int(pos), eval(item, {"__builtins__": self.safe_builtins}, self.variables))
                        self.output.append(f"List {list_name} is now: {self.variables[list_name]}")
                    except Exception as e:
                        self.output.append(f"Couldn't modify list: {str(e)}")
                else:
                    self.output.append(f"{list_name} is not a list")

            # Conditional statements with better string handling
            elif line.startswith('If'):
                match = re.match(r'If (.*?), (.*?)(?:\s+else\s+(.*))?$', line)
                if match:
                    condition, true_action, false_action = match.groups()
                    condition = self.translate_condition(condition)
                    try:
                        if eval(condition, {"__builtins__": self.safe_builtins}, self.variables):
                            # Process the true action
                            self.process_line(true_action.strip())
                        elif false_action:
                            # Process the false action
                            self.process_line(false_action.strip())
                    except Exception as e:
                        self.output.append(f"Error in if statement: {str(e)}")

            # Function calls
            elif match := re.match(r'Call (\w+)(?: with (.*))?', line):
                func_name, args = match.groups()
                if func_name in self.functions:
                    try:
                        args_list = [eval(arg.strip(), {"__builtins__": self.safe_builtins}, self.variables) 
                                   for arg in (args.split(',') if args else [])]
                        result = self.functions[func_name](*args_list)
                        if result is not None:
                            self.output.append(str(result))
                    except Exception as e:
                        self.output.append(f"Error calling function: {str(e)}")
                else:
                    self.output.append(f"Function {func_name} not found")

            else:
                self.output.append(f"I don't understand: {line}")

        except Exception as e:
            self.output.append(f"Error: {str(e)}")

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