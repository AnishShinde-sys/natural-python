import re
import math
import random
from typing import Dict, Any, List
import logging
import traceback

# Configure logging with a detailed format and multiple handlers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('interpreter.log')  # Logs to a file named interpreter.log
    ]
)
logger = logging.getLogger(__name__)

class AdvancedInterpreter:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.output: List[str] = []
        self.safe_builtins = {}
        
        # Initialize safe built-in functions
        self._init_extended_builtins()

        # Define command patterns for various operations
        # Order is important: more specific patterns should come first to avoid overlaps
        self.command_patterns = {
            'create_var': [
                r'(?:Make|Create|Set|Let|Define|Give me) (?:a |an |the )?(?:new )?(?:number|string|list|dict|set|variable)? ?(?:called |named |as )?(\w+) (?:equal to|to|be|as|with|with value|that is) (.*)',
                r'(?:Let|Set) (\w+) (?:be|equal|to) (.*)',
            ],
            'print': [
                r'(?:Print|Show|Display|Output|Tell me|What is|Say)(?: the| a| an)? (?:value of )?(?:variable )?([^,]+)',
            ],
            'math_ops': [
                r'(?:Add|Plus|Increase) (\d+(?:\.\d+)?|\w+) (?:to|into) (\w+)',
                r'(?:Multiply) (\w+) by (\d+(?:\.\d+)?|\w+)',
                r'(?:Divide) (\w+) by (\d+(?:\.\d+)?|\w+)',
                r'(?:Double) (\w+)',
            ],
            'string_ops': [
                r'Convert (\w+) to (uppercase|lowercase)',
                r'Join (\w+) with (?:["\'])(.+?)(?:["\'])',
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
                r'Format string (?:["\'])(.+?)(?:["\']) with (?:["\'])(.+?)(?:["\'])',
            ],
            'conditional': [
                r'If (.*?) is (bigger than|less than|equal to) (\d+):',
            ],
        }

    def _init_extended_builtins(self):
        """Initialize safe built-in functions for evaluation"""
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

    def process_line(self, line: str):
        """Process a single line of natural language input"""
        try:
            line = line.strip()
            logger.info(f"Processing line: {line}")
            
            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        logger.info(f"Matched pattern in category: {category}")
                        if category == 'create_var':
                            name, value = match.groups()
                            return self.create_variable(name, value)
                        elif category == 'print':
                            var_name = match.group(1)
                            return self.print_value(var_name)
                        elif category == 'math_ops':
                            if 'Double' in pattern:
                                var_name = match.group(1)
                                return self.math_operation('double', None, var_name)
                            else:
                                amount, var_name = match.groups()
                                operation = self._determine_math_operation(line)
                                return self.math_operation(operation, amount, var_name)
                        elif category == 'string_ops':
                            var_name, operation = match.groups()
                            return self.string_operation(var_name, operation)
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

    def process_code(self, code: str) -> str:
        """Process multiple lines of code and return the accumulated output"""
        self.output = []
        try:
            logger.info("Starting code processing")
            logger.debug(f"Input code:\n{code}")
            
            # Split the code into individual lines
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
                        # Collect indented lines under the condition
                        while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                            block_lines.append(lines[i].strip())
                            i += 1
                        # Evaluate the condition and execute the block if True
                        if self.evaluate_condition(condition):
                            for block_line in block_lines:
                                self.process_line(block_line)
                        continue  # Skip the increment at the end
                    else:
                        # Process a single line
                        self.process_line(line)
                i += 1
            return '\n'.join(self.output)
        except Exception as e:
            # Log and append any errors encountered during code processing
            error_msg = f"Error processing code: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error: {str(e)}")
            return '\n'.join(self.output)

    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition translated to Python syntax"""
        try:
            # Translate natural language condition to Python condition
            condition = self.translate_condition(condition)
            logger.info(f"Evaluating condition: {condition}")
            return eval(condition, {"__builtins__": self.safe_builtins}, self.variables)
        except Exception as e:
            # Log and append any errors encountered during condition evaluation
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
            # Log and append any errors encountered during variable creation
            error_msg = f"Error creating variable '{name}': {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error creating variable: {str(e)}")

    def print_value(self, value: str):
        """Print a value or variable"""
        try:
            clean_value = value.strip()
            if clean_value in self.variables:
                # Print the value of a variable
                self.output.append(str(self.variables[clean_value]))
            else:
                try:
                    # Attempt to evaluate the value as a Python expression
                    result = eval(clean_value, {"__builtins__": self.safe_builtins}, self.variables)
                    self.output.append(str(result))
                except:
                    # If evaluation fails, print the raw string
                    self.output.append(clean_value)
        except Exception as e:
            # Log and append any errors encountered during printing
            self.output.append(f"Error printing value: {str(e)}")
            logger.error(f"Error in print_value: {str(e)}")

    def math_operation(self, operation: str, amount: Any, var_name: str):
        """Handle basic math operations like add, subtract, multiply, divide, double, half"""
        try:
            if var_name not in self.variables:
                self.output.append(f"I can't find a variable called {var_name}")
                logger.error(f"Variable '{var_name}' not found among variables: {list(self.variables.keys())}")
                return

            original = self.variables[var_name]
            logger.debug(f"Original value of '{var_name}': {original} (type: {type(original)})")
            
            # Handle the 'double' and 'half' operations separately
            if operation in ['double', 'half']:
                if not isinstance(original, (int, float)):
                    self.output.append(f"Cannot perform '{operation}' on non-numeric variable '{var_name}'")
                    logger.error(f"Variable '{var_name}' is not numeric for operation '{operation}'")
                    return

                if operation == 'double':
                    result = original * 2
                elif operation == 'half':
                    result = original / 2

                self.variables[var_name] = result
                self.output.append(f"Updated {var_name} from {original} to {result}")
                logger.info(f"Performed '{operation}' on '{var_name}': {original} -> {result}")
                return

            # For other operations, ensure the original value is numeric
            if not isinstance(original, (int, float)):
                self.output.append(f"Cannot perform '{operation}' on non-numeric variable '{var_name}'")
                logger.error(f"Variable '{var_name}' is not numeric for operation '{operation}'")
                return

            # Determine the amount value
            if isinstance(amount, str):
                if amount in self.variables:
                    amount_val = self.variables[amount]
                elif self.is_number(amount):
                    amount_val = float(amount)
                else:
                    self.output.append(f"I can't find a variable called {amount}")
                    logger.error(f"Amount '{amount}' is not a number or variable")
                    return
            else:
                amount_val = float(amount)

            result = None

            if operation == 'add':
                result = original + amount_val
            elif operation == 'subtract':
                result = original - amount_val
            elif operation == 'multiply':
                result = original * amount_val
            elif operation == 'divide':
                if amount_val == 0:
                    self.output.append("Cannot divide by zero")
                    logger.error("Division by zero attempted")
                    return
                result = original / amount_val

            self.variables[var_name] = result
            self.output.append(f"Updated {var_name} from {original} to {result}")
            logger.info(f"Performed '{operation}' on '{var_name}': {original} -> {result}")

        except Exception as e:
            # Log and append any unexpected errors during math operations
            error_msg = f"Error in math operation: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            self.output.append(f"Error in math operation: {str(e)}")

    def string_operation(self, var_name: str, operation: str):
        """Handle string operations like converting to uppercase or lowercase"""
        try:
            if var_name not in self.variables:
                self.output.append(f"I can't find a string called {var_name}")
                logger.error(f"String '{var_name}' not found among variables: {list(self.variables.keys())}")
                return

            value = self.variables[var_name]
            logger.debug(f"Original value of '{var_name}': {value} (type: {type(value)})")
            
            if not isinstance(value, str):
                self.output.append(f"'{var_name}' is not a string")
                logger.error(f"Variable '{var_name}' is not a string for string operation")
                return

            if operation.lower() == 'uppercase':
                result = value.upper()
            elif operation.lower() == 'lowercase':
                result = value.lower()
            else:
                self.output.append(f"Unknown string operation: {operation}")
                logger.error(f"Unknown string operation '{operation}'")
                return

            self.variables[var_name] = result
            self.output.append(f"Converted {var_name} to {operation}: {result}")
            logger.info(f"Performed '{operation}' on '{var_name}': {value} -> {result}")

        except Exception as e:
            self.output.append(f"Error in string operation: {str(e)}")
            logger.error(f"Error in string_operation: {str(e)}")

    def string_join(self, var_name: str, text: str):
        """Handle joining a string with another string"""
        try:
            if var_name not in self.variables:
                self.output.append(f"I can't find a string called {var_name}")
                logger.error(f"String '{var_name}' not found among variables: {list(self.variables.keys())}")
                return

            value = self.variables[var_name]
            logger.debug(f"Original value of '{var_name}': {value} (type: {type(value)})")
            
            if not isinstance(value, str):
                self.output.append(f"'{var_name}' is not a string")
                logger.error(f"Variable '{var_name}' is not a string for string joining")
                return

            # Remove surrounding quotes if present
            text = text.strip('"\'')
            result = value + text
            self.variables[var_name] = result
            self.output.append(f"Joined {var_name} with \"{text}\": {result}")
            logger.info(f"Joined '{var_name}' with \"{text}\": {result}")

        except Exception as e:
            # Log and append any errors encountered during string joining
            self.output.append(f"Error in string join: {str(e)}")
            logger.error(f"Error in string_join: {str(e)}")

    def list_operation(self, operation: str, value: Any, var_name: str):
        """Handle list operations like add, remove, sort"""
        try:
            if var_name not in self.variables:
                self.output.append(f"I can't find a list called {var_name}")
                logger.error(f"List '{var_name}' not found among variables: {list(self.variables.keys())}")
                return

            lst = self.variables[var_name]
            logger.debug(f"Original list '{var_name}': {lst} (type: {type(lst)})")
            
            if not isinstance(lst, list):
                self.output.append(f"'{var_name}' is not a list")
                logger.error(f"Variable '{var_name}' is not a list for list operation")
                return

            if operation == 'add' or operation == 'append':
                # Handle quoted strings by removing quotes
                if isinstance(value, str) and value.startswith(("'", '"')) and value.endswith(("'", '"')):
                    element = value[1:-1]  # Remove quotes
                else:
                    try:
                        element = int(value)
                    except ValueError:
                        try:
                            element = float(value)
                        except ValueError:
                            element = value
                lst.append(element)
                self.output.append(f"Added {element} to {var_name}: {lst}")
                logger.info(f"Added {element} to list '{var_name}': {lst}")

            elif operation == 'remove':
                try:
                    element = int(value)
                except ValueError:
                    element = value.strip('"\'')
                if element in lst:
                    lst.remove(element)
                    self.output.append(f"Removed {element} from {var_name}: {lst}")
                    logger.info(f"Removed {element} from list '{var_name}': {lst}")
                else:
                    self.output.append(f"{element} not found in {var_name}")
                    logger.warning(f"Element '{element}' not found in list '{var_name}' for removal")

            elif operation == 'sort':
                try:
                    lst.sort()
                    self.output.append(f"Sorted {var_name}: {lst}")
                    logger.info(f"Sorted list '{var_name}': {lst}")
                except TypeError:
                    self.output.append(f"Cannot sort {var_name} due to incompatible types")
                    logger.error(f"TypeError when trying to sort list '{var_name}'")

            else:
                self.output.append(f"Unknown list operation: {operation}")
                logger.error(f"Unknown list operation '{operation}'")
                return

            self.variables[var_name] = lst

        except Exception as e:
            # Log and append any unexpected errors during list operations
            self.output.append(f"Error in list operation: {str(e)}")
            logger.error(f"Error in list_operation: {str(e)}")

    def math_function(self, func: str, value: Any):
        """Handle advanced math functions like square root, maximum, and random number generation"""
        try:
            func = func.lower()
            if func in ['square root', 'sqrt']:
                result = math.sqrt(float(value))
                self.output.append(f"Square root of {value} is {result}")
                logger.info(f"Calculated square root of {value}: {result}")
            elif func in ['maximum', 'max']:
                if value in self.variables and isinstance(self.variables[value], list):
                    result = max(self.variables[value])
                    self.output.append(f"Maximum of {value} is {result}")
                    logger.info(f"Calculated maximum of list '{value}': {result}")
                else:
                    self.output.append(f"{value} is not a list or doesn't exist")
                    logger.warning(f"List '{value}' not found or not a list for maximum calculation")
            elif func == 'random':
                try:
                    start, end = map(int, value.split(','))
                except ValueError:
                    start, end = 1, 100  # Default range if parsing fails
                    logger.warning(f"Failed to parse range for random number. Using default range {start}-{end}")
                result = random.randint(start, end)
                self.output.append(f"Generated random number between {start} and {end}: {result}")
                logger.info(f"Generated random number between {start} and {end}: {result}")
            else:
                self.output.append(f"Unknown math function: {func}")
                logger.error(f"Unknown math function '{func}'")
        except Exception as e:
            # Log and append any unexpected errors during math functions
            self.output.append(f"Error in math function: {str(e)}")
            logger.error(f"Error in math_function method: {str(e)}")

    def string_format(self, template: str, value: str):
        """Handle string formatting"""
        try:
            formatted = template.format(value.strip('"\''))
            self.output.append(formatted)
            logger.info(f"Formatted string: {formatted}")
        except Exception as e:
            # Log and append any errors encountered during string formatting
            self.output.append(f"Error formatting string: {str(e)}")
            logger.error(f"Error in format_string method: {str(e)}")

    def _clean_variable_name(self, name: str) -> str:
        """Clean and validate variable name"""
        clean_name = name.strip().replace(' ', '_')
        if not clean_name.isidentifier():
            raise ValueError(f"Invalid variable name: {name}")
        return clean_name

    def is_number(self, s: str) -> bool:
        """Check if a string represents a number"""
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _determine_math_operation(self, line: str) -> str:
        """Helper method to determine the math operation from the command"""
        if re.search(r'Add|Plus|Increase', line, re.IGNORECASE):
            return 'add'
        elif re.search(r'Subtract|Minus|Decrease', line, re.IGNORECASE):
            return 'subtract'
        elif re.search(r'Multiply', line, re.IGNORECASE):
            return 'multiply'
        elif re.search(r'Divide', line, re.IGNORECASE):
            return 'divide'
        return 'unknown'

    def handle_conditional(self, var_name: str, operator: str, value: str):
        """Handle conditional statements"""
        try:
            if var_name not in self.variables:
                self.output.append(f"I can't find a variable called {var_name}")
                return False
            
            var_value = self.variables[var_name]
            value = float(value)
            
            if operator == 'bigger than':
                return var_value > value
            elif operator == 'less than':
                return var_value < value
            elif operator == 'equal to':
                return var_value == value
                
        except Exception as e:
            self.output.append(f"Error in conditional: {str(e)}")
            logger.error(f"Error in handle_conditional: {str(e)}")
            return False
 