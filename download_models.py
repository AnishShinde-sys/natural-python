import nltk
import spacy

def download_models():
    # Download NLTK data
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
    
    # Download spaCy model
    spacy.cli.download("en_core_web_sm")

if __name__ == "__main__":
    download_models() 