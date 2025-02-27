import re
import math
import random
from typing import Dict, Any, List
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('interpreter.log')
    ]
)
logger = logging.getLogger(__name__)

class AdvancedInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.output: List[str] = []
        
        # Initialize safe built-in functions
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
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'math': math,
            'random': random,
        }

        # Define command patterns
        self.command_patterns = {
            'create_var': [
                r'(?:Make|Create|Set|Let|Define) (?:a |an |the )?(?:new )?(?:number|string|list|dict|set|variable)? ?(?:called |named |as )?(\w+) (?:equal to|to|be|as|with) (.*)',
            ],
            'print': [
                r'(?:Print|Show|Display|Output) (?:the )?(?:value of )?([^,]+)',
                r'(?:Print|Show|Display|Output) ["\'](.+?)["\']',
            ],
            'math_ops': [
                r'(?:Add|Plus|Increase) (\d+(?:\.\d+)?|\w+) (?:to|into) (\w+)',
                r'(?:Multiply) (\w+) by (\d+(?:\.\d+)?|\w+)',
                r'(?:Divide) (\w+) by (\d+(?:\.\d+)?|\w+)',
                r'(?:Double) (\w+)',
            ],
            'string_ops': [
                r'Convert (\w+) to (uppercase|lowercase)',
                r'Join (\w+) with ["\'](.+?)["\']',
            ],
            'list_ops': [
                r'(?:Add|Append) (\d+|\w+|(?:["\']).*?(?:["\'])) to (\w+)',
                r'(?:Remove) (\d+|\w+|(?:["\']).*?(?:["\'])) from (\w+)',
                r'Sort (\w+)',
            ],
            'math_funcs': [
                r'Calculate(?: the)? square root of (\d+)',
                r'Find(?: the)? maximum of (\w+)',
                r'Generate(?: a)? random number between (\d+)(?:,| and )(\d+)',
            ],
            'string_format': [
                r'Format string ["\'](.+?)["\'] with ["\'](.+?)["\']',
            ],
            'conditional': [
                r'If (.*?) is (bigger than|less than|equal to) (\d+):',
            ],
        }

    def process_code(self, code: str) -> str:
        """Process multiple lines of code"""
        self.output = []
        try:
            lines = code.strip().split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    if line.lower().startswith('if') and line.endswith(':'):
                        # Handle conditional blocks
                        condition = line[2:-1].strip()
                        block_lines = []
                        i += 1
                        while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                            block_lines.append(lines[i].strip())
                            i += 1
                        if self.evaluate_condition(condition):
                            for block_line in block_lines:
                                self.process_line(block_line)
                        continue
                    else:
                        self.process_line(line)
                i += 1
            return '\n'.join(self.output)
        except Exception as e:
            error_msg = f"Error processing code: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.output.append(f"Error: {str(e)}")
            return '\n'.join(self.output)

    def process_line(self, line: str):
        """Process a single line of natural language input"""
        try:
            line = line.strip()
            logger.info(f"Processing line: {line}")
            
            # Handle direct string printing first
            if line.startswith(('Print', 'Show', 'Display', 'Output')) and ('"' in line or "'" in line):
                match = re.match(r'(?:Print|Show|Display|Output) ["\'](.+?)["\']', line)
                if match:
                    self.output.append(match.group(1))
                    return

            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        logger.info(f"Matched pattern in category: {category}")
                        if category == 'create_var':
                            name, value = match.groups()
                            return self.create_variable(name, value)
                        elif category == 'print':
                            var_name = match.group(1).strip()
                            return self.print_value(var_name)
                        elif category == 'math_ops':
                            if 'Double' in pattern:
                                var_name = match.group(1)
                                return self.math_operation('double', 2, var_name)
                            else:
                                if 'Multiply' in line or 'Divide' in line:
                                    var_name, amount = match.groups()
                                else:
                                    amount, var_name = match.groups()
                                operation = self._determine_math_operation(line)
                                return self.math_operation(operation, amount, var_name)
                        elif category == 'string_ops':
                            if 'Convert' in line:
                                var_name, operation = match.groups()
                                return self.string_operation(var_name, operation)
                            elif 'Join' in line:
                                var_name, text = match.groups()
                                return self.string_join(var_name, text)
                        elif category == 'list_ops':
                            if 'Sort' in pattern:
                                var_name = match.group(1)
                                return self.list_operation('sort', None, var_name)
                            else:
                                value, var_name = match.groups()
                                operation = 'add' if 'Add' in line else 'remove'
                                return self.list_operation(operation, value, var_name)
                        elif category == 'math_funcs':
                            if 'random' in pattern:
                                start, end = match.groups()
                                return self.math_function('random', f"{start},{end}")
                            elif 'square root' in pattern:
                                value = match.group(1)
                                return self.math_function('sqrt', value)
                            else:
                                value = match.group(1)
                                return self.math_function('max', value)
                        elif category == 'string_format':
                            template, value = match.groups()
                            return self.string_format(template, value)
                        elif category == 'conditional':
                            var_name, operator, value = match.groups()
                            return self.handle_conditional(var_name, operator, value)

            logger.warning(f"No matching pattern found for: {line}")
            self.output.append(f"I don't understand: {line}")

        except Exception as e:
            error_msg = f"Error processing line: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error: {str(e)}")

    def _determine_math_operation(self, line: str) -> str:
        """Helper method to determine the math operation from the command"""
        if re.search(r'Add|Plus|Increase', line, re.IGNORECASE):
            return 'add'
        elif re.search(r'Multiply', line, re.IGNORECASE):
            return 'multiply'
        elif re.search(r'Divide', line, re.IGNORECASE):
            return 'divide'
        elif re.search(r'Double', line, re.IGNORECASE):
            return 'double'
        return 'unknown'

    def create_variable(self, name: str, value: str):
        """Create a variable with the given name and value"""
        try:
            logger.info(f"Creating variable '{name}' with value: {value}")
            clean_value = value.strip('"\'')
            try:
                # Attempt to evaluate the value as a Python expression
                evaluated_value = eval(clean_value, {"__builtins__": self.safe_builtins}, self.variables)
                logger.debug(f"Evaluated value: {evaluated_value} (type: {type(evaluated_value)})")
            except Exception as eval_error:
                # If evaluation fails, treat the value as a raw string
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

    def math_operation(self, operation: str, amount: Any, var_name: str):
        """Handle basic math operations"""
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            original = self.variables[var_name]
            if not isinstance(original, (int, float)):
                self.output.append(f"Cannot perform math operation on non-numeric value: {var_name}")
                return

            # Convert amount to number if it's a string
            if isinstance(amount, str):
                try:
                    amount = float(amount)
                except ValueError:
                    if amount in self.variables:
                        amount = self.variables[amount]
                    else:
                        self.output.append(f"Invalid number: {amount}")
                        return

            result = None
            if operation == 'add':
                result = original + amount
            elif operation == 'multiply':
                result = original * amount
            elif operation == 'divide':
                if amount == 0:
                    self.output.append("Cannot divide by zero")
                    return
                result = original / amount
            elif operation == 'double':
                result = original * 2

            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} from {original} to {result}")

        except Exception as e:
            self.output.append(f"Error in math operation: {str(e)}")
            logger.error(f"Error in math_operation: {str(e)}")

    def string_operation(self, var_name: str, operation: str):
        """Handle string operations"""
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            value = self.variables[var_name]
            if not isinstance(value, str):
                self.output.append(f"Cannot perform string operation on non-string value: {var_name}")
                return

            if operation.lower() == 'uppercase':
                result = value.upper()
                self.variables[var_name] = result
                self.output.append(f"Updated {var_name} to {result}")
            elif operation.lower() == 'lowercase':
                result = value.lower()
                self.variables[var_name] = result
                self.output.append(f"Updated {var_name} to {result}")
            else:
                self.output.append(f"Unknown string operation: {operation}")

        except Exception as e:
            self.output.append(f"Error in string operation: {str(e)}")
            logger.error(f"Error in string_operation: {str(e)}")

    def string_join(self, var_name: str, text: str):
        """Handle joining strings"""
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            value = self.variables[var_name]
            if not isinstance(value, str):
                self.output.append(f"Cannot join non-string value: {var_name}")
                return

            text = text.strip('"\'')
            result = value + text
            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} to {result}")

        except Exception as e:
            self.output.append(f"Error joining strings: {str(e)}")
            logger.error(f"Error in string_join: {str(e)}")

    def list_operation(self, operation: str, value: Any, var_name: str):
        """Handle list operations"""
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return

            lst = self.variables[var_name]
            if not isinstance(lst, list):
                self.output.append(f"Cannot perform list operation on non-list value: {var_name}")
                return

            if operation == 'add':
                try:
                    element = int(value)
                except ValueError:
                    try:
                        element = float(value)
                    except ValueError:
                        element = value.strip('"\'')
                
                lst.append(element)
                self.variables[var_name] = lst
                self.output.append(f"Updated {var_name} to {lst}")

            elif operation == 'remove':
                try:
                    element = int(value)
                except ValueError:
                    element = value.strip('"\'')
                
                if element in lst:
                    lst.remove(element)
                    self.variables[var_name] = lst
                    self.output.append(f"Updated {var_name} to {lst}")
                else:
                    self.output.append(f"Element {element} not found in {var_name}")

            elif operation == 'sort':
                try:
                    lst.sort()
                    self.variables[var_name] = lst
                    self.output.append(f"Updated {var_name} to {lst}")
                except TypeError:
                    self.output.append(f"Cannot sort {var_name} - list contains mixed types")

        except Exception as e:
            self.output.append(f"Error in list operation: {str(e)}")
            logger.error(f"Error in list_operation: {str(e)}")

    def math_function(self, func: str, value: Any):
        """Handle advanced math functions"""
        try:
            if func == 'sqrt':
                try:
                    num = float(value)
                    result = math.sqrt(num)
                    self.output.append(f"Square root of {value} is {result}")
                except ValueError:
                    self.output.append(f"Cannot calculate square root of non-numeric value: {value}")
            
            elif func == 'max':
                if value in self.variables and isinstance(self.variables[value], list):
                    try:
                        result = max(self.variables[value])
                        self.output.append(f"Maximum of {value} is {result}")
                    except TypeError:
                        self.output.append(f"Cannot find maximum of list with mixed types")
                else:
                    self.output.append(f"'{value}' is not a list")
            
            elif func == 'random':
                try:
                    start, end = map(int, value.split(','))
                    result = random.randint(start, end)
                    self.output.append(f"Generated random number between {start} and {end}: {result}")
                except ValueError:
                    self.output.append(f"Invalid range for random number: {value}")
            
            else:
                self.output.append(f"Unknown math function: {func}")
                
        except Exception as e:
            self.output.append(f"Error in math function: {str(e)}")
            logger.error(f"Error in math_function: {str(e)}")

    def string_format(self, template: str, value: str):
        """Handle string formatting"""
        try:
            # Remove quotes from template and value
            template = template.strip('"\'')
            value = value.strip('"\'')
            
            # Format the string
            try:
                formatted = template.format(value)
                self.output.append(formatted)
            except KeyError:
                self.output.append(f"Invalid format string: {template}")
            except IndexError:
                self.output.append(f"Missing values for format string: {template}")
                
        except Exception as e:
            self.output.append(f"Error formatting string: {str(e)}")
            logger.error(f"Error in string_format: {str(e)}")

    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition translated to Python syntax"""
        try:
            # Translate natural language condition to Python condition
            condition = self.translate_condition(condition)
            logger.info(f"Evaluating condition: {condition}")
            return eval(condition, {"__builtins__": self.safe_builtins}, self.variables)
        except Exception as e:
            self.output.append(f"Error evaluating condition: {str(e)}")
            logger.error(f"Error in evaluate_condition method: {str(e)}")
            return False

    def translate_condition(self, condition: str) -> str:
        """Translate natural language conditions to Python syntax"""
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

        for phrase, symbol in translations.items():
            condition = condition.replace(phrase, symbol)
        logger.info(f"Translated condition to Python syntax: {condition}")
        return condition

    def handle_conditional(self, var_name: str, operator: str, value: str) -> bool:
        """Handle conditional statements"""
        try:
            if var_name not in self.variables:
                self.output.append(f"Variable '{var_name}' not found")
                return False
            
            var_value = self.variables[var_name]
            try:
                value = float(value)
            except ValueError:
                self.output.append(f"Cannot compare with non-numeric value: {value}")
                return False
            
            if operator == 'bigger than':
                return var_value > value
            elif operator == 'less than':
                return var_value < value
            elif operator == 'equal to':
                return var_value == value
            else:
                self.output.append(f"Unknown comparison operator: {operator}")
                return False
                
        except Exception as e:
            self.output.append(f"Error in conditional: {str(e)}")
            logger.error(f"Error in handle_conditional: {str(e)}")
            return False
 