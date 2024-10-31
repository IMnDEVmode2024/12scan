import spacy

# Load a pre-trained spaCy model
nlp_model = spacy.load("en_core_web_sm")

def extract_entities(text):
    # Process the text and extract entities
    doc = nlp_model(text)
    entities = [{"entity": ent.text, "type": ent.label_} for ent in doc.ents]
    return entities