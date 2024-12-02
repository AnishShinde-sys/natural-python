import re
import datetime
import math
import json
import random
from typing import Dict, Any, List
import logging
import traceback
import sys

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('interpreter.log')
    ]
)
logger = logging.getLogger(__name__)

class AdvancedInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.output: List[str] = []
        self.safe_builtins = {}
        
        # Initialize built-in functions
        self._init_extended_builtins()

        # Command patterns with core functionality
        self.command_patterns = {
            'create_var': [
                r'(?:Make|Create|Set|Let|Define|Give me) (?:a |an |the )?(?:new )?(?:number|string|list|dict|set|variable)? ?(?:called |named |as )?(\w+) (?:equal to|to|be|as|with|with value|that is) (.*)',
                r'(?:Let|Set) (\w+) (?:be|equal|to) (.*)',
            ],
            'print': [
                r'(?:Print|Show|Display|Output|Tell me|What is|Say)(?: the| a| an)? (?:value of )?(?:variable )?([^,]+)',
                r'(?:Print|Show|Display|Output|Say) ["\'](.+)["\']',
                r'(?:What is|Tell me|Show me)(?: the)? (?:value of )?(.+)',
            ],
            'math_ops': [
                r'(?:Add|Plus|Increase) (.*?) (?:to|into) (\w+)',
                r'(?:Subtract|Minus|Decrease) (.*?) from (\w+)',
                r'(?:Multiply|Times) (\w+) by (.*)',
                r'(?:Divide) (\w+) by (.*)',
            ],
            'string_ops': [
                r'(?:Convert|Make|Change) (\w+) (?:to|into) (uppercase|lowercase)',
                r'(?:Join|Combine|Concatenate) (\w+) with ["\'](.+)["\']',
            ],
            'list_ops': [
                r'(?:Add|Append) (\d+) to (\w+)',
                r'(?:Remove) (\d+) from (\w+)',
                r'(?:Sort) (\w+)',
            ],
            'math_funcs': [
                r'(?:Calculate|Compute|Find)(?: the)? square root of (\d+)',
                r'(?:Find|Get|Calculate)(?: the)? maximum of (\w+)',
                r'Generate(?: a)? random number between (\d+) and (\d+)',
            ],
            'string_format': [
                r'Format string ["\'](.+)["\'] with ["\'](.+)["\']',
            ],
        }

    def _init_extended_builtins(self):
        """Initialize safe built-in functions"""
        self.safe_builtins = {
            'abs': abs,
            'len': len,
            'max': max,
            'min': min,
            'sum': sum,
            'round': round,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'math': math,
        }

    def process_line(self, line: str):
        """Process a single line of natural language input"""
        try:
            line = ' '.join(line.split())
            logger.info(f"Processing line: {line}")
            
            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        logger.info(f"Matched category: {category} with pattern: {pattern}")
                        logger.debug(f"Match groups: {match.groups()}")
                        
                        if category == 'create_var':
                            name, value = match.groups()[-2:]  # Get last two groups
                            name = self._clean_variable_name(name)
                            return self.create_variable(name, value)
                        
                        elif category == 'print':
                            to_print = match.group(1)
                            return self.print_value(to_print)
                        
                        elif category == 'math_ops':
                            operation = pattern.split()[0].lower()
                            if operation in ['multiply', 'divide']:
                                var_name, amount = match.groups()
                            else:
                                amount, var_name = match.groups()
                            return self.math_operation(operation, amount, var_name)
                        
                        elif category == 'string_ops':
                            if 'Convert' in pattern:
                                var_name, operation = match.groups()
                                return self.string_operation(var_name, operation)
                            else:
                                var_name, text = match.groups()
                                return self.string_join(var_name, text)
                        
                        elif category == 'list_ops':
                            operation = pattern.split()[0].lower()
                            if operation == 'sort':
                                var_name = match.group(1)
                                return self.list_operation(operation, None, var_name)
                            else:
                                value, var_name = match.groups()
                                return self.list_operation(operation, value, var_name)
                        
                        elif category == 'math_funcs':
                            if 'square root' in pattern:
                                number = match.group(1)
                                return self.math_function('sqrt', number)
                            elif 'maximum' in pattern:
                                var_name = match.group(1)
                                return self.math_function('max', var_name)
                            else:
                                start, end = match.groups()
                                return self.math_function('random', f"{start},{end}")
                        
                        elif category == 'string_format':
                            template, value = match.groups()
                            return self.string_format(template, value)
            
            logger.warning(f"No matching pattern found for input: {line}")
            logger.debug(f"Available patterns: {self.command_patterns}")
            self.output.append(f"I don't understand: {line}")

        except Exception as e:
            error_msg = f"Error processing line: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error: {str(e)}")

    def create_variable(self, name: str, value: str):
        """Create a variable with given name and value"""
        try:
            logger.info(f"Creating variable '{name}' with value: {value}")
            clean_value = value.strip('"\'')
            try:
                evaluated_value = eval(clean_value, {"__builtins__": self.safe_builtins}, self.variables)
                logger.debug(f"Evaluated value: {evaluated_value} (type: {type(evaluated_value)})")
            except Exception as eval_error:
                logger.warning(f"Failed to evaluate value, using raw string. Error: {eval_error}")
                evaluated_value = clean_value

            self.variables[name] = evaluated_value
            self.output.append(f"Created {name} = {evaluated_value}")
            logger.info(f"Successfully created variable: {name} = {evaluated_value}")
            
        except Exception as e:
            error_msg = f"Error creating variable '{name}': {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error creating variable: {str(e)}")

    def print_value(self, value: str):
        """Print a value or variable"""
        try:
            clean_value = value.strip()
            if clean_value in self.variables:
                self.output.append(str(self.variables[clean_value]))
            else:
                try:
                    result = eval(clean_value, {"__builtins__": self.safe_builtins}, self.variables)
                    self.output.append(str(result))
                except:
                    self.output.append(clean_value)
        except Exception as e:
            self.output.append(f"Error printing value: {str(e)}")
            logger.error(f"Error in print_value: {str(e)}")

    def math_operation(self, operation: str, amount: str, var_name: str):
        """Handle basic math operations"""
        try:
            logger.info(f"Attempting {operation} operation on {var_name} with amount {amount}")
            
            if var_name not in self.variables:
                logger.error(f"Variable '{var_name}' not found in variables: {list(self.variables.keys())}")
                self.output.append(f"Variable '{var_name}' not found")
                return

            try:
                amount_val = float(amount) if amount.replace('.','').isdigit() else self.variables[amount]
                logger.debug(f"Parsed amount value: {amount_val} (type: {type(amount_val)})")
            except ValueError as ve:
                logger.error(f"Failed to convert amount '{amount}' to number: {str(ve)}")
                self.output.append(f"Invalid amount: {amount}")
                return
            except KeyError as ke:
                logger.error(f"Amount variable '{amount}' not found in variables: {str(ke)}")
                self.output.append(f"Variable '{amount}' not found")
                return

            original = self.variables[var_name]
            logger.debug(f"Original value of {var_name}: {original} (type: {type(original)})")
            
            if not isinstance(original, (int, float)):
                logger.error(f"Variable '{var_name}' is not a number (type: {type(original)})")
                self.output.append(f"'{var_name}' is not a number")
                return

            result = None
            if operation == 'add':
                result = original + amount_val
            elif operation == 'subtract':
                result = original - amount_val
            elif operation == 'multiply':
                result = original * amount_val
            elif operation == 'divide':
                if amount_val == 0:
                    logger.error("Division by zero attempted")
                    self.output.append("Cannot divide by zero")
                    return
                result = original / amount_val

            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} = {result}")
            logger.info(f"Successfully performed {operation}: {var_name} {operation} {amount_val} = {result}")

        except Exception as e:
            error_msg = f"Error in math operation: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error in math operation: {str(e)}")

    def string_operation(self, var_name: str, operation: str):
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            value = self.variables[var_name]
            if not isinstance(value, str):
                self.output.append(f"'{var_name}' is not a string")
                return

            if operation.lower() == 'uppercase':
                result = value.upper()
            elif operation.lower() == 'lowercase':
                result = value.lower()

            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} = {result}")

        except Exception as e:
            self.output.append(f"Error in string operation: {str(e)}")

    def string_join(self, var_name: str, text: str):
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            value = self.variables[var_name]
            if not isinstance(value, str):
                self.output.append(f"'{var_name}' is not a string")
                return

            result = value + text.strip('"\'')
            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} = {result}")

        except Exception as e:
            self.output.append(f"Error in string join: {str(e)}")

    def list_operation(self, operation: str, value: str, var_name: str):
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            lst = self.variables[var_name]
            if not isinstance(lst, list):
                self.output.append(f"'{var_name}' is not a list")
                return

            if operation == 'add':
                lst.append(int(value))
            elif operation == 'remove':
                lst.remove(int(value))
            elif operation == 'sort':
                lst.sort()

            self.variables[var_name] = lst
            self.output.append(f"Updated {var_name} = {lst}")

        except Exception as e:
            self.output.append(f"Error in list operation: {str(e)}")

    def math_function(self, func: str, value: str):
        try:
            if func == 'sqrt':
                result = math.sqrt(float(value))
                self.output.append(f"Square root of {value} is {result}")
            elif func == 'max':
                if value not in self.variables or not isinstance(self.variables[value], list):
                    self.output.append(f"'{value}' is not a list")
                    return
                result = max(self.variables[value])
                self.output.append(f"Maximum of {value} is {result}")
            elif func == 'random':
                start, end = map(int, value.split(','))
                result = random.randint(start, end)
                self.output.append(f"Random number between {start} and {end}: {result}")

        except Exception as e:
            self.output.append(f"Error in math function: {str(e)}")

    def string_format(self, template: str, value: str):
        try:
            result = template.format(value.strip('"\''))
            self.output.append(result)
        except Exception as e:
            self.output.append(f"Error in string format: {str(e)}")

    def _clean_variable_name(self, name: str) -> str:
        """Clean and validate variable name"""
        clean_name = name.strip().replace(' ', '_')
        if not clean_name.isidentifier():
            raise ValueError(f"Invalid variable name: {name}")
        return clean_name

    def process_code(self, code: str) -> str:
        """Process multiple lines of code and return output"""
        self.output = []
        try:
            logger.info("Starting code processing")
            logger.debug(f"Input code:\n{code}")
            
            lines = code.strip().split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    logger.info(f"Processing line {i}: {line}")
                    self.process_line(line)
                else:
                    logger.debug(f"Skipping line {i}: {line}")
            
            output = '\n'.join(self.output)
            logger.info("Code processing completed successfully")
            logger.debug(f"Final output:\n{output}")
            return output
            
        except Exception as e:
            error_msg = f"Error processing code: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            return f"Error: {str(e)}"
