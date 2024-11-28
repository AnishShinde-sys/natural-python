from flask import Flask, render_template, request, jsonify
import re
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from typing import Dict, List, Any
from datetime import datetime
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

@dataclass
class Variable:
    name: str
    value: Any
    type: str
    created_at: datetime

class CodeInterpreter(ABC):
    @abstractmethod
    def process_code(self, code: str) -> str:
        pass

class NaturalPythonInterpreter(CodeInterpreter):
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.output: List[str] = []
        self.lemmatizer = WordNetLemmatizer()
        
    def preprocess_text(self, text: str) -> str:
        """Apply NLP preprocessing to the input text"""
        # Tokenization and lemmatization
        tokens = word_tokenize(text.lower())
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Use spaCy for advanced NLP
        doc = nlp(text)
        
        # Extract important entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Return processed text
        return " ".join(lemmatized)

    def process_code(self, natural_code: str) -> str:
        self.output = []
        
        # Process the code using NLP
        processed_code = self.preprocess_text(natural_code)
        
        # Process each line
        for line in natural_code.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                self.process_line(line.strip())
                
        return '\n'.join(self.output)

    def process_line(self, line: str) -> None:
        try:
            # Variable creation with type inference
            if match := re.match(r'Make (?:a )?(?:number |string |list |dict )?called (\w+) equal to (.*)', line):
                name, value = match.groups()
                try:
                    evaluated_value = eval(value, {"__builtins__": {}}, 
                                        {k: v.value for k, v in self.variables.items()})
                    
                    # Create Variable object with type information
                    var_type = type(evaluated_value).__name__
                    self.variables[name] = Variable(
                        name=name,
                        value=evaluated_value,
                        type=var_type,
                        created_at=datetime.now()
                    )
                    self.output.append(
                        f"Created {name} of type {var_type} with value {evaluated_value}"
                    )
                except Exception as e:
                    self.output.append(f"Error creating variable {name}: {str(e)}")
            
            # Enhanced print with type information
            elif line.startswith(('Print', 'Show', 'Display')):
                var_name = line.split()[-1]
                if var_name in self.variables:
                    var = self.variables[var_name]
                    self.output.append(
                        f"{var_name} ({var.type}) = {var.value} "
                        f"(created at {var.created_at.strftime('%H:%M:%S')})"
                    )
                else:
                    self.output.append(f"Variable {var_name} not found")
            
            # Mathematical operations with type checking
            elif match := re.match(r'(Add|Subtract|Multiply|Divide) (\d+) (?:to|from|by) (\w+)', line):
                operation, amount, var_name = match.groups()
                if var_name in self.variables:
                    var = self.variables[var_name]
                    if var.type not in ('int', 'float'):
                        self.output.append(f"Cannot perform {operation} on {var.type}")
                        return
                    
                    amount = float(amount)
                    if operation == 'Add':
                        var.value += amount
                    elif operation == 'Subtract':
                        var.value -= amount
                    elif operation == 'Multiply':
                        var.value *= amount
                    elif operation == 'Divide':
                        if amount == 0:
                            self.output.append("Cannot divide by zero")
                            return
                        var.value /= amount
                    
                    self.output.append(
                        f"{operation}ed {amount} to {var_name}. New value: {var.value}"
                    )
                else:
                    self.output.append(f"Variable {var_name} not found")
            
            # Enhanced if statements with multiple conditions
            elif line.startswith('If'):
                match = re.match(r'If (.*?), (.*)', line)
                if match:
                    condition, action = match.groups()
                    condition = self.translate_condition(condition)
                    try:
                        if eval(condition, {"__builtins__": {}}, 
                              {k: v.value for k, v in self.variables.items()}):
                            self.process_line(action)
                    except Exception as e:
                        self.output.append(f"Error in condition: {str(e)}")
            
            else:
                # Use spaCy for better understanding of unknown commands
                doc = nlp(line)
                self.output.append(
                    f"Unknown command. Detected intent: "
                    f"{[(token.text, token.pos_) for token in doc]}"
                )
                
        except Exception as e:
            self.output.append(f"Error processing line: {str(e)}")

    def translate_condition(self, condition: str) -> str:
        """Enhanced condition translation with more operations"""
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
            'or': 'or'
        }
        
        for phrase, operator in translations.items():
            condition = condition.replace(phrase, operator)
        return condition

# Flask app setup with security
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, force_https=True)
interpreter = NaturalPythonInterpreter()

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    output = interpreter.process_code(code)
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)