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
        self._init_extended_builtins()

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
                # More natural math operations
                r'(?:What is|Calculate|Find) (.*?) (?:plus|minus|times|divided by) (.*)',
                r'(?:Increase|Decrease) (.*?) by (.*?) percent',
                r'(?:Take|Find)(?: the)? (.*?) percent of (.*)',
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
            'data_types': [
                # Type conversion
                r'(?:Convert|Change|Transform|Make) (.*?) (?:to|into|as)(?: a| an)? (string|int|float|bool|list|tuple|set|dict)',
                r'(?:Get|Show|Tell me)(?: the)? type of (.*)',
            ],
            'string_ops': [
                # String operations
                r'(?:Join|Combine|Concatenate) (.*?) (?:and|with) (.*)',
                r'(?:Split|Break|Divide) (.*?) (?:by|at|on) (.*)',
                r'(?:Make|Convert)(?: the)? (.*?) (?:uppercase|lowercase|capital|title case)',
                r'(?:Count|Find|Get)(?: the)? (?:number of|occurrences of) (.*?) in (.*)',
            ],
            'collections': [
                # List/Set/Dict operations
                r'(?:Create|Make|Define)(?: a| an)? (list|set|dict|tuple) (?:called|named) (\w+)(?: with)? (.*)',
                r'(?:Get|Find|Show)(?: the)? (length|size|count) of (.*)',
                r'(?:Sort|Order|Arrange) (.*?) (?:in)? (ascending|descending) order',
                r'(?:Reverse|Flip|Invert) (?:the list|the array|the sequence)? (.*)',
            ],
            'loops': [
                # For loops
                r'(?:For|For each|Loop through) (.*?) in (.*?):',
                r'(?:Repeat|Do|Execute) (.*?) times:',
                # While loops
                r'(?:While|As long as|Until) (.*?):',
                r'(?:Keep|Continue) (?:going|running|executing) (?:while|as long as) (.*?):',
            ],
            'functions': [
                # Function definition
                r'(?:Define|Create|Make)(?: a)? function (?:called |named )?(\w+)(?:\((.*?)\))?(?: that| to| which)? (.*?):',
                r'(?:Call|Run|Execute|Use)(?: the)? function (\w+)(?: with)? (.*)',
                # Lambda functions
                r'(?:Create|Make|Define)(?: a)? quick function (?:that|to) (.*)',
            ],
            'classes': [
                # Class definition and inheritance
                r'(?:Create|Define|Make)(?: a)? class (?:called |named )?(\w+)(?:(?: that)? inherits from| extends) (.*?):',
                r'(?:Create|Define|Make)(?: a)? class (?:called |named )?(\w+):',
                # Object creation
                r'(?:Create|Make|Instantiate)(?: a| an)? (\w+) object (?:called |named )?(\w+)(?: with)? (.*)',
            ],
            'error_handling': [
                # Try-except blocks
                r'(?:Try|Attempt)(?: to)? (.*?)(?:: or| otherwise| if it fails,) (.*)',
                r'(?:Handle|Catch)(?: the)? error(?:s)?(?: when| if) (.*)',
            ],
            'file_ops': [
                # File operations
                r'(?:Read|Open|Load)(?: the)? file (?:called |named )?(.*)',
                r'(?:Write|Save|Store) (.*?) (?:to|in)(?: the)? file (?:called |named )?(.*)',
                r'(?:Append|Add) (.*?) (?:to|in)(?: the)? file (?:called |named )?(.*)',
            ],
            'modules': [
                # Module operations
                r'(?:Import|Use|Include)(?: the)? module (?:called |named )?(.*)',
                r'(?:Import|Use|Include) (.*?) from (?:the )?module (.*)',
            ],
            'datetime_ops': [
                # Date and time operations
                r'(?:Get|Show|Display)(?: the)? current (?:date|time|datetime)',
                r'(?:Format|Convert)(?: the)? date (.*?) (?:to|as) (.*)',
            ],
            'math_extended': [
                # Extended math operations
                r'(?:Calculate|Compute|Find)(?: the)? (sin|cos|tan|log|exp) of (.*)',
                r'(?:Round|Floor|Ceil) (?:the )?(?:number )?(.*)',
                r'(?:Get|Find|Calculate)(?: the)? (absolute|factorial|power) of (.*)',
            ],
            'input': [
                # Basic input with natural language
                r'(?:Ask|Get|Request|Input)(?: for)?(?: the| a| an)? (.*?)(?:from the user| from user)?',
                r'(?:Get|Request|Input)(?: the| a| an)? (.*?) (?:from|by) (?:the )?user',
                r'(?:Let|Have)(?: the)? user (?:input|enter|type|give|provide)(?: a| an)? (.*)',
            ],
            'string_format': [
                r'(?:Format|Make)(?: the)? string (.*?) (?:with|using) (.*)',
                r'(?:Replace|Substitute) (.*?) (?:with|by|for) (.*?) in (.*)',
                r'(?:Put|Insert) (.*?) (?:into|in) (?:the )?(?:string|text) (.*)',
            ],
            'syntax': [
                # Basic Python syntax
                r'(?:Show|Display|Explain)(?: the)? syntax (?:for|of) (.*)',
                r'(?:How|What is)(?: the)? (?:correct )?way to (write|use|do) (.*)',
            ],
            'comments': [
                # Comment operations
                r'(?:Add|Create|Make)(?: a)? comment (?:saying|with|that says) (.*)',
                r'(?:Add|Create|Make)(?: a)? multiline comment(?: with)? (.*)',
            ],
            'casting': [
                # Type casting
                r'(?:Cast|Convert|Change) (.*?) to (?:a |an )?(int|float|str|bool|list|tuple|set|dict)',
                r'(?:Make|Turn) (.*?) into (?:a |an )?(int|float|str|bool|list|tuple|set|dict)',
            ],
            'boolean_ops': [
                # Boolean operations
                r'(?:Check|Is|Are) (.*?) (?:equal to|same as|different from|greater than|less than) (.*)',
                r'(?:Compare|Test) if (.*?) (?:is|are) (.*)',
            ],
            'iterators': [
                # Iterator operations
                r'(?:Create|Make|Get)(?: an)? iterator (?:for|from) (.*)',
                r'(?:Get|Fetch)(?: the)? next (?:item|value|element) (?:from|of) (.*)',
            ],
            'polymorphism': [
                # Polymorphic operations
                r'(?:Create|Define|Make)(?: a)? method (.*?) (?:that|to) override(?:s)? (.*)',
                r'(?:Override|Redefine|Replace) (?:the )?method (.*?) (?:in|of) (.*)',
            ],
            'scope': [
                # Scope operations
                r'(?:Create|Define|Make)(?: a)? (global|local|nonlocal) variable (?:called |named )?(.*)',
                r'(?:Use|Access|Get)(?: the)? (global|local|nonlocal) (?:version of |copy of )?(.*)',
            ],
            'json_ops': [
                # JSON operations
                r'(?:Convert|Transform|Change) (.*?) to JSON',
                r'(?:Parse|Read|Load) JSON (?:from|in) (.*)',
                r'(?:Save|Write|Store) (.*?) as JSON(?: to| in)? (.*)',
            ],
            'regex_ops': [
                # Regular expression operations
                r'(?:Find|Search|Match) pattern (.*?) in (.*)',
                r'(?:Replace|Substitute) (.*?) with (.*?) using regex (.*)',
                r'(?:Split|Break)(?: the)? text (.*?) (?:using|with) regex (.*)',
            ],
            'pip_ops': [
                # PIP operations
                r'(?:Install|Add|Get)(?: the)? package (.*?)(?:(?: with)? version (.*?))?',
                r'(?:Uninstall|Remove|Delete) package (.*)',
                r'(?:List|Show|Display)(?: all)? installed packages',
            ],
            'array_ops': [
                # Array operations
                r'(?:Create|Make|Initialize)(?: an)? array (?:called |named )?(.*?)(?:(?: with)? values? (.*?))?',
                r'(?:Get|Access|Fetch) element (?:at |index )?(.*?) from array (.*)',
                r'(?:Set|Put|Place) value (.*?) at (?:index |position )?(.*?) in array (.*)',
            ]
        }

        # Add more translations for conditions
        self.condition_translations = {
            'is between': 'lambda x: {min} <= x <= {max}',
            'contains': 'in',
            'starts with': 'startswith',
            'ends with': 'endswith',
            'matches': 'match',
            'is empty': 'not',
            'has length': 'len',
            'is instance of': 'isinstance',
            'has attribute': 'hasattr',
            'can be called': 'callable',
            'is subclass of': 'issubclass',
            'is iterable': 'iter',
            'is a number': 'isinstance(x, (int, float))',
            'is a string': 'isinstance(x, str)',
            'is callable': 'callable',
        }

        # Initialize additional built-ins
        self._init_extended_builtins()

    def _init_extended_builtins(self):
        """Initialize additional built-in functions and modules"""
        self.safe_builtins.update({
            # Type checking
            'isinstance': isinstance,
            'issubclass': issubclass,
            'hasattr': hasattr,
            'callable': callable,
            'iter': iter,
            'next': next,
            
            # JSON operations
            'json': {
                'loads': json.loads,
                'dumps': json.dumps,
                'load': json.load,
                'dump': json.dump
            },
            
            # Regular expressions
            're': {
                'match': re.match,
                'search': re.search,
                'findall': re.findall,
                'sub': re.sub,
                'split': re.split,
                'compile': re.compile
            },
            
            # Additional type conversions
            'bool': bool,
            'bytes': bytes,
            'bytearray': bytearray,
            'complex': complex,
            'frozenset': frozenset,
            
            # Additional built-in functions
            'all': all,
            'any': any,
            'chr': chr,
            'ord': ord,
            'bin': bin,
            'hex': hex,
            'oct': oct,
            'id': id,
            'hash': hash,
            'repr': repr,
        })

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

            # Add handling for input patterns
            if match := re.match(self.command_patterns['input'][0], line, re.IGNORECASE):
                prompt = match.group(1)
                return self.get_user_input(prompt)
                
            # Add handling for string formatting
            if match := re.match(self.command_patterns['string_format'][0], line, re.IGNORECASE):
                template, values = match.groups()
                return self.format_string(template, values)

            # If no pattern matched, try to understand as a natural expression
            self.output.append(f"I don't understand: {line}")

        except Exception as e:
            self.output.append(f"Error: {str(e)}")

    def _determine_math_operation(self, pattern: str) -> str:
        """
        Determine the math operation from the pattern with comprehensive Python operation support
        and natural language handling.
        """
        operations = {
            # Basic Arithmetic
            'Add': [
                'add', 'plus', 'increase', 'increment', 'combine', 'sum',
                'raise by', 'grow by', 'expand by', 'augment by', '+'
            ],
            'Subtract': [
                'subtract', 'minus', 'decrease', 'decrement', 'reduce',
                'take away', 'remove', 'lower by', 'diminish by', 'deduct', '-'
            ],
            'Multiply': [
                'multiply', 'times', 'scale', 'product', '*',
                'multiply by', 'scale by', 'amplify by', 'x'
            ],
            'Divide': [
                'divide', 'split', 'share', 'quotient', '/',
                'divide by', 'split by', 'distribute by'
            ],
            
            # Extended Math Operations
            'Power': [
                'power', 'exponent', 'squared', 'cubed', '**',
                'raise to', 'to the power of', 'exponential'
            ],
            'Root': [
                'root', 'sqrt', 'square root', 'cube root',
                'nth root', 'radical'
            ],
            'Modulo': [
                'modulo', 'remainder', 'mod', '%',
                'modulus', 'remainder of'
            ],
            'FloorDiv': [
                'floor divide', 'integer divide', '//',
                'divide with floor', 'integer division'
            ],
            
            # Numeric Shortcuts
            'Double': [
                'double', 'twice', 'multiply by 2', '×2',
                'make twice as big'
            ],
            'Triple': [
                'triple', 'thrice', 'multiply by 3', '×3',
                'make three times as big'
            ],
            'Half': [
                'half', 'halve', 'divide by 2', '÷2',
                'make half as big'
            ],
            'Quarter': [
                'quarter', 'fourth', 'divide by 4', '÷4',
                'make a quarter as big'
            ],
            
            # Percentage Operations
            'Percentage': [
                'percent of', 'percentage of', '%',
                'increase by percent', 'decrease by percent'
            ],
            
            # Bitwise Operations
            'BitwiseAnd': [
                'bitwise and', 'bit and', '&',
                'and bits', 'binary and'
            ],
            'BitwiseOr': [
                'bitwise or', 'bit or', '|',
                'or bits', 'binary or'
            ],
            'BitwiseXor': [
                'bitwise xor', 'bit xor', '^',
                'xor bits', 'binary xor'
            ],
            'BitwiseNot': [
                'bitwise not', 'bit not', '~',
                'not bits', 'binary not'
            ],
            'LeftShift': [
                'left shift', 'shift left', '<<',
                'binary left shift'
            ],
            'RightShift': [
                'right shift', 'shift right', '>>',
                'binary right shift'
            ],
            
            # Rounding Operations
            'Round': [
                'round', 'round to', 'round off',
                'round to nearest', 'approximate'
            ],
            'Floor': [
                'floor', 'round down', 'floor value',
                'round towards negative'
            ],
            'Ceil': [
                'ceil', 'ceiling', 'round up',
                'round towards positive'
            ],
            
            # Statistical Operations
            'Absolute': [
                'absolute', 'abs', 'absolute value',
                'magnitude', 'distance from zero'
            ],
            'Maximum': [
                'maximum', 'max', 'largest',
                'biggest', 'highest'
            ],
            'Minimum': [
                'minimum', 'min', 'smallest',
                'least', 'lowest'
            ],
            
            # Natural Language Variations
            'Increase': [
                'increase', 'make bigger', 'raise', 'grow',
                'enhance', 'boost', 'elevate'
            ],
            'Decrease': [
                'decrease', 'make smaller', 'lower', 'reduce',
                'diminish', 'shrink', 'lessen'
            ],
            'Negate': [
                'negate', 'make negative', 'opposite',
                'reverse sign', 'change sign'
            ]
        }
        
        pattern_lower = pattern.lower()
        
        # First try exact matches
        for op, keywords in operations.items():
            if any(keyword == pattern_lower for keyword in keywords):
                return op
            
        # Then try partial matches
        for op, keywords in operations.items():
            if any(keyword in pattern_lower for keyword in keywords):
                return op
            
        # Handle special compound cases
        if 'times bigger' in pattern_lower:
            return 'Multiply'
        if 'times smaller' in pattern_lower:
            return 'Divide'
        if 'percent more' in pattern_lower:
            return 'PercentageIncrease'
        if 'percent less' in pattern_lower:
            return 'PercentageDecrease'
        
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
                # Handle numeric literals first - improved handling
                if isinstance(amount, (int, float)):
                    amount_val = float(amount)
                elif str(amount).replace('.', '', 1).isdigit():
                    amount_val = float(amount)
                # Then handle variable references
                elif amount in self.variables:
                    amount_val = float(self.variables[amount])
                # Finally try evaluation with stripped quotes
                else:
                    clean_amount = amount.strip('"\'')
                    try:
                        amount_val = float(eval(clean_amount, {"__builtins__": self.safe_builtins}, self.variables))
                    except:
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
                    try:
                        # Convert original to float if it's a number
                        orig_val = float(original) if isinstance(original, (int, str)) else original
                        result = operations[operation](orig_val, amount_val)
                        if result is not None:
                            self.variables[var_name] = result
                            self.output.append(f"Updated {var_name} from {original} to {result}")
                        else:
                            self.output.append(f"Cannot divide by zero")
                    except ValueError:
                        # Handle string concatenation for Add operation
                        if operation == 'Add' and isinstance(original, str):
                            result = str(original) + str(amount_val)
                            self.variables[var_name] = result
                            self.output.append(f"Updated {var_name} from {original} to {result}")
                        else:
                            self.output.append(f"Cannot perform {operation} on {var_name}")
                else:
                    self.output.append(f"Unknown operation: {operation}")

            except ValueError as ve:
                self.output.append(f"Cannot convert {amount} to a number: {str(ve)}")
            except Exception as e:
                self.output.append(f"Error in math operation: {str(e)}")

        except Exception as e:
            self.output.append(f"Error in math operation: {str(e)}")

    def process_code(self, code: str) -> str:
        """Process multiple lines of code"""
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
            condition = first_line[2:-1].strip() if first_line.endswith(':') else first_line[2:].strip()
            indented_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            try:
                condition = self._clean_condition(condition)
                condition = self.translate_condition(condition)
                
                if eval(condition, {"__builtins__": self.safe_builtins}, self.variables):
                    for line in indented_lines:
                        self.process_line(line)
            except Exception as e:
                self.output.append(f"Error in if statement: {str(e)}")

    def create_variable(self, name: str, value: str):
        """Handle variable creation with improved error handling"""
        try:
            # Clean the value string
            value = value.strip()
            
            # Try to evaluate the value
            try:
                evaluated_value = eval(value, {"__builtins__": self.safe_builtins}, self.variables)
            except:
                # If evaluation fails, treat as string literal
                evaluated_value = value.strip('"\'')
            
            self.variables[name] = evaluated_value
            self.output.append(f"Created {name} = {evaluated_value}")
        except Exception as e:
            self.output.append(f"I couldn't create {name}. {str(e)}")

    def print_value(self, to_print: str):
        """Handle printing values with improved string handling"""
        to_print = to_print.strip()
        try:
            # Handle string literals
            if (to_print.startswith('"') and to_print.endswith('"')) or \
               (to_print.startswith("'") and to_print.endswith("'")):
                self.output.append(to_print[1:-1])
            # Handle math constants
            elif to_print == 'pi':
                self.output.append(str(self.safe_builtins['math']['pi']))
            # Handle variables and expressions
            else:
                if to_print in self.variables:
                    result = self.variables[to_print]
                else:
                    result = eval(to_print, {"__builtins__": self.safe_builtins}, self.variables)
                self.output.append(str(result))
        except Exception as e:
            self.output.append(f"I couldn't show {to_print}. {str(e)}")

    def translate_condition(self, condition: str) -> str:
        """Translate natural language conditions to Python"""
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
        
        for phrase, operator in translations.items():
            condition = condition.replace(phrase, operator)
        
        # Clean up spaces around operators
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

    def process_function(self, name: str, params: str, body: List[str]):
        """Handle function definition and execution"""
        try:
            # Clean parameters
            params = [p.strip() for p in params.split(',') if p.strip()]
            
            # Create function body
            func_body = []
            for line in body:
                processed_line = self.process_line(line)
                if processed_line:
                    func_body.append(processed_line)

            # Store function
            self.functions[name] = {
                'params': params,
                'body': func_body
            }
            self.output.append(f"Created function {name}")

        except Exception as e:
            self.output.append(f"Error creating function: {str(e)}")

    def process_class(self, name: str, parent: str = None, body: List[str] = None):
        """Handle class definition and inheritance"""
        try:
            class_dict = {'methods': {}, 'parent': parent}
            
            if body:
                for line in body:
                    if line.strip().startswith('Define function'):
                        # Process method definition
                        method_match = re.match(r'Define function (\w+)\((.*?)\):(.*)', line)
                        if method_match:
                            method_name, params, method_body = method_match.groups()
                            class_dict['methods'][method_name] = {
                                'params': params.split(','),
                                'body': method_body
                            }

            self.classes[name] = class_dict
            self.output.append(f"Created class {name}" + 
                             (f" inheriting from {parent}" if parent else ""))

        except Exception as e:
            self.output.append(f"Error creating class: {str(e)}")

    def get_user_input(self, prompt: str) -> str:
        """Handle user input with improved natural language support"""
        try:
            # Clean and format the prompt
            clean_prompt = prompt.strip()
            # Remove common words that don't add meaning
            for word in ['the', 'a', 'an', 'some', 'for']:
                clean_prompt = re.sub(rf'\b{word}\b', '', clean_prompt)
            clean_prompt = ' '.join(clean_prompt.split())
            
            # Format the prompt nicely
            formatted_prompt = f"Enter {clean_prompt}: "
            
            # In a web context, we need to handle this differently
            # Store the fact that we're waiting for input
            self.variables['_waiting_for_input'] = True
            self.variables['_input_prompt'] = formatted_prompt
            
            # For web interface, return a special message
            self.output.append(f"Waiting for input: {formatted_prompt}")
            return '_waiting_for_input'

        except Exception as e:
            self.output.append(f"Error getting input: {str(e)}")
            return None

    def process_input(self, user_input: str):
        """Process user input and store it in variables"""
        try:
            if '_waiting_for_input' in self.variables and self.variables['_waiting_for_input']:
                # Try to evaluate the input if it looks like a number or expression
                try:
                    if user_input.replace('.', '').isdigit():
                        value = float(user_input)
                    elif all(c in '0123456789+-*/.()' for c in user_input):
                        value = eval(user_input, {"__builtins__": self.safe_builtins}, {})
                    else:
                        value = user_input
                    
                    # Store the input in a variable if specified
                    if '_input_variable' in self.variables:
                        var_name = self.variables['_input_variable']
                        self.variables[var_name] = value
                        self.output.append(f"Stored input in {var_name}: {value}")
                    
                    # Clean up input state
                    del self.variables['_waiting_for_input']
                    if '_input_prompt' in self.variables:
                        del self.variables['_input_prompt']
                    if '_input_variable' in self.variables:
                        del self.variables['_input_variable']
                    
                    return value
                
                except Exception as e:
                    self.output.append(f"Error processing input: {str(e)}")
                    return None
            else:
                self.output.append("No input was requested")
                return None
            
        except Exception as e:
            self.output.append(f"Error processing input: {str(e)}")
            return None

    def format_string(self, template: str, values: str, target: str = None):
        """Handle string formatting with natural language support"""
        try:
            # Handle different formatting styles
            if '{' in template and '}' in template:
                # Python format-style string
                if isinstance(values, dict):
                    result = template.format(**values)
                elif isinstance(values, (list, tuple)):
                    result = template.format(*values)
                else:
                    result = template.format(values)
            else:
                # Simple replacement
                if target:
                    result = template.replace(target, str(values))
                else:
                    result = template % values if '%' in template else template + str(values)
            
            if target:
                self.variables[target] = result
                self.output.append(f"Updated {target} = {result}")
            else:
                self.output.append(result)

        except Exception as e:
            self.output.append(f"Error formatting string: {str(e)}")

    def list_operation(self, operation: str, value: str, list_name: str, position: int = None):
        """Handle list operations with improved value handling"""
        try:
            if list_name not in self.variables:
                self.output.append(f"I can't find a list called {list_name}")
                return

            if not isinstance(self.variables[list_name], list):
                self.output.append(f"{list_name} is not a list")
                return

            # Process the value
            if isinstance(value, str):
                if value.startswith('"') or value.startswith("'"):
                    processed_value = value.strip('"\'')
                elif value in self.variables:
                    processed_value = self.variables[value]
                else:
                    try:
                        # Try to evaluate as a literal or expression
                        processed_value = eval(value, {"__builtins__": self.safe_builtins}, self.variables)
                    except:
                        processed_value = value  # Use raw value if evaluation fails

            current_list = self.variables[list_name]

            if operation == 'Add':
                current_list.append(processed_value)
                self.output.append(f"Added {processed_value} to {list_name}")
            elif operation == 'Remove':
                if processed_value in current_list:
                    current_list.remove(processed_value)
                    self.output.append(f"Removed {processed_value} from {list_name}")
                else:
                    self.output.append(f"Could not find {processed_value} in {list_name}")
            elif operation == 'Insert':
                try:
                    pos = int(position) if position else 0
                    if 0 <= pos <= len(current_list):
                        current_list.insert(pos, processed_value)
                        self.output.append(f"Inserted {processed_value} at position {pos} in {list_name}")
                    else:
                        self.output.append(f"Position {pos} is out of range for {list_name}")
                except (ValueError, TypeError):
                    self.output.append(f"Invalid position: {position}")

        except Exception as e:
            self.output.append(f"Error in list operation: {str(e)}")

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

@app.route('/input', methods=['POST'])
def handle_input():
    try:
        user_input = request.json.get('input', '')
        if not user_input.strip():
            return jsonify({'error': 'No input provided'})
            
        result = interpreter.process_input(user_input)
        return jsonify({
            'output': interpreter.output,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error handling input: {str(e)}")
        return jsonify({'error': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)