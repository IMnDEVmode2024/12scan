import spacy
from typing import List, Dict

class NLPProcessor:
    def __init__(self):
        """Initialize the NLP processor with the English language model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model isn't installed, provide helpful error
            raise OSError(
                "The English language model isn't installed. "
                "Please install it with: python -m spacy download en_core_web_sm"
            )

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text
        
        Args:
            text (str): The input text to process
            
        Returns:
            List[Dict]: List of dictionaries containing entities and their types
        """
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                # Filter for relevant entity types
                if ent.label_ in ['GPE', 'LOC', 'FAC', 'ORG', 'PERSON']:
                    entities.append({
                        'entity': ent.text,
                        'type': ent.label_
                    })
            
            return entities
            
        except Exception as e:
            print(f"Error in entity extraction: {str(e)}")
            return []

    def get_entity_types(self) -> List[str]:
        """
        Get list of available entity types
        
        Returns:
            List[str]: List of entity type labels
        """
        return ['GPE', 'LOC', 'FAC', 'ORG', 'PERSON']

# For backwards compatibility
nlp_model = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> List[Dict]:
    """
    Legacy function for backwards compatibility
    """
    doc = nlp_model(text)
    entities = [{"entity": ent.text, "type": ent.label_} for ent in doc.ents]
    return entities
