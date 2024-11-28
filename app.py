from flask import Flask, render_template, request, jsonify
import re
from typing import Dict, List, Any
from datetime import datetime
import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize NLP components lazily
nlp = None
lemmatizer = None

def download_nltk_data():
    """Download NLTK data to a specified directory"""
    import nltk
    
    # Set NLTK data path to a writable directory
    nltk_data_dir = os.path.join(os.getcwd(), 'nltk_data')
    os.environ['NLTK_DATA'] = nltk_data_dir
    os.makedirs(nltk_data_dir, exist_ok=True)
    
    try:
        # Download required NLTK data
        for package in ['punkt', 'wordnet']:
            try:
                nltk.download(package, download_dir=nltk_data_dir, quiet=True)
            except Exception as e:
                logger.error(f"Error downloading {package}: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Failed to download NLTK data: {str(e)}")
        raise

def init_nlp():
    """Initialize NLP components if not already initialized"""
    global nlp, lemmatizer
    try:
        if nlp is None:
            import spacy
            logger.info("Loading spaCy model...")
            try:
                nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading spaCy model: {str(e)}")
                raise
            
        if lemmatizer is None:
            import nltk
            from nltk.stem import WordNetLemmatizer
            
            # Download NLTK data if needed
            download_nltk_data()
            
            lemmatizer = WordNetLemmatizer()
            logger.info("NLTK components initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing NLP components: {str(e)}")
        raise

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
        
    def preprocess_text(self, text: str) -> str:
        """Apply NLP preprocessing to the input text"""
        try:
            init_nlp()  # Initialize NLP components if needed
            from nltk.tokenize import word_tokenize
            
            # Tokenization and lemmatization
            tokens = word_tokenize(text.lower())
            lemmatized = [lemmatizer.lemmatize(token) for token in tokens]
            
            # Use spaCy for advanced NLP
            doc = nlp(text)
            
            # Extract important entities
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Return processed text
            return " ".join(lemmatized)
        except Exception as e:
            logger.error(f"Error in text preprocessing: {str(e)}")
            return text  # Return original text if processing fails

    def process_code(self, natural_code: str) -> str:
        try:
            self.output = []
            
            # Process each line
            for line in natural_code.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    self.process_line(line.strip())
                    
            return '\n'.join(self.output)
        except Exception as e:
            error_msg = f"Error processing code: {str(e)}"
            logger.error(error_msg)
            return error_msg

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

# Flask app setup with better error handling
app = Flask(__name__)
interpreter = NaturalPythonInterpreter()

@app.before_first_request
def before_first_request():
    """Initialize NLP components before first request"""
    try:
        init_nlp()
    except Exception as e:
        logger.error(f"Failed to initialize NLP components: {str(e)}")
        # Continue even if initialization fails
        pass

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/run_code', methods=['POST'])
def run_code():
    try:
        code = request.json.get('code', '')
        if not code.strip():
            return jsonify({'output': 'No code to run'})
            
        output = interpreter.process_code(code)
        return jsonify({'output': output})
    except Exception as e:
        logger.error(f"Error running code: {str(e)}")
        return jsonify({'error': f"Error running code: {str(e)}"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'nlp_initialized': nlp is not None,
        'lemmatizer_initialized': lemmatizer is not None
    })

@app.errorhandler(500)
def handle_500(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({'error': 'Internal Server Error'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled Exception: {str(error)}")
    return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    # Initialize NLP components at startup in development
    try:
        init_nlp()
    except Exception as e:
        logger.error(f"Failed to initialize NLP components at startup: {str(e)}")
    
    app.run(debug=True)