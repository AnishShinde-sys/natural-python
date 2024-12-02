import re
from typing import List, Dict
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class TextProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        
    def process_text(self, text: str) -> Dict:
        """Process text using various Python concepts"""
        # Strings and RegEx
        cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Lists and List Comprehension
        tokens = word_tokenize(cleaned_text)
        lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Sets for unique words
        unique_words = set(lemmatized)
        
        # Dictionary to store word frequencies
        word_freq = {}
        for word in lemmatized:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        return {
            'original': text,
            'cleaned': cleaned_text,
            'tokens': tokens,
            'lemmatized': lemmatized,
            'unique_words': list(unique_words),
            'word_frequencies': word_freq
        } 