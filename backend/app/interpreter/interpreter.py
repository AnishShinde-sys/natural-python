import re
import datetime
import math
import json
import random
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
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
            ]
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
                        logger.info(f"Matched category: {category}")
                        
                        if category == 'create_var':
                            name, value = match.groups()[-2:]  # Get last two groups
                            name = self._clean_variable_name(name)
                            return self.create_variable(name, value)
                        
                        elif category == 'print':
                            to_print = match.group(1)
                            return self.print_value(to_print)
                        
                        elif category == 'math_ops':
                            operation = pattern.split()[0].lower()
                            amount, var_name = match.groups()
                            return self.math_operation(operation, amount, var_name)
            
            self.output.append(f"I don't understand: {line}")
            logger.warning(f"No pattern match for: {line}")

        except Exception as e:
            self.output.append(f"Error: {str(e)}")
            logger.error(f"Error processing line: {str(e)}")

    def create_variable(self, name: str, value: str):
        """Create a variable with given name and value"""
        try:
            clean_value = value.strip('"\'')
            try:
                evaluated_value = eval(clean_value, {"__builtins__": self.safe_builtins}, self.variables)
            except:
                evaluated_value = clean_value

            self.variables[name] = evaluated_value
            self.output.append(f"Created {name} = {evaluated_value}")
            logger.info(f"Created variable: {name} = {evaluated_value}")
        except Exception as e:
            self.output.append(f"Error creating variable: {str(e)}")
            logger.error(f"Error in create_variable: {str(e)}")

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
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            try:
                amount_val = float(amount) if amount.replace('.','').isdigit() else self.variables[amount]
            except:
                self.output.append(f"Invalid amount: {amount}")
                return

            original = self.variables[var_name]
            if not isinstance(original, (int, float)):
                self.output.append(f"'{var_name}' is not a number")
                return

            if operation == 'add':
                result = original + amount_val
            elif operation == 'subtract':
                result = original - amount_val
            elif operation == 'multiply':
                result = original * amount_val
            elif operation == 'divide':
                if amount_val == 0:
                    self.output.append("Cannot divide by zero")
                    return
                result = original / amount_val

            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} = {result}")
            logger.info(f"Math operation: {var_name} {operation} {amount_val} = {result}")

        except Exception as e:
            self.output.append(f"Error in math operation: {str(e)}")
            logger.error(f"Error in math_operation: {str(e)}")

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
            lines = code.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.process_line(line)
            return '\n'.join(self.output)
        except Exception as e:
            logger.error(f"Error processing code: {str(e)}")
            return f"Error: {str(e)}"
