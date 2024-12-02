import spacy
import nltk
from datetime import datetime
import json
import re
import numpy as np
from text_processor import TextProcessor
from nlp_analyzer import NLPAnalyzer
from data_structures import DataStructureDemo
from advanced_concepts import AdvancedPythonDemo

def main():
    # Initialize NLP models
    nlp = spacy.load("en_core_web_sm")
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')

    # Create instances of our custom classes
    text_processor = TextProcessor()
    nlp_analyzer = NLPAnalyzer(nlp)
    data_demo = DataStructureDemo()
    advanced_demo = AdvancedPythonDemo()

    # Example text for processing
    sample_text = """
    Natural Language Processing (NLP) is a branch of artificial intelligence
    that helps computers understand, interpret, and manipulate human language.
    This example demonstrates various Python concepts while processing text.
    """

    # Demonstrate text processing
    processed_text = text_processor.process_text(sample_text)
    nlp_results = nlp_analyzer.analyze_text(processed_text)
    
    # Show results
    print_results(nlp_results)

def print_results(results):
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main() 