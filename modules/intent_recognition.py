import sys
import os
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from config import MODEL_DIR
from modules.output import voice_assistant

class IntentRecognizer:
    def load_model_and_tokenizer(self, model_dir=MODEL_DIR):
        required_files = [
            "config.json", "model.safetensors", "special_tokens_map.json",
            "tokenizer.json", "tokenizer_config.json", "vocab.txt"
        ]
        for file in required_files:
            if not os.path.exists(os.path.join(model_dir, file)):
                raise FileNotFoundError(f"Missing file: {file} in {model_dir}")

        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        classifier = pipeline('text-classification', model=model, tokenizer=tokenizer)
        return model, tokenizer, classifier

    def process_input(self,text, classifier, label_map, regex_patterns):
        result = classifier(text)[0]
        intent = label_map.get(result['label'], "unknown")
        confidence = result['score']
    
        entity = "None"
        if intent in regex_patterns:
            match = re.search(regex_patterns[intent], text, re.IGNORECASE)
            entity = match.group(1) if match else "None"
    
        return {"intent": intent, "entity": entity, "confidence": round(confidence, 4)}

    def recognize(self, input_text):
        intents = [
            "create_file", "create_folder", "open_application", "web_search",
            "download_file", "system_command", "exit"
        ]
        label_map = {f"LABEL_{i}": intent for i, intent in enumerate(intents)}
    
        regex_patterns = {
            "create_file": r"(?:create|make|generate|I need)\s+(?:a\s+)?(?:file|document)\s+(?:named|called)?\s*([\w\-\.]+\.[\w]+)",
            "create_folder": r"(?:create|make|set up|new)\s+(?:a\s+)?(?:folder|directory)\s+(?:for|named|called)?\s*([\w\-]+)",
            "open_application": r"(?:open|start|launch|run)\s+(?:the\s+)?([\w\s]+?)(?:\s+application|\s+app)?(?:\s+now)?",
            "web_search": r"(?:search|find|look up)(?:\s+for|\s+the\s+internet\s+for)?\s+(.+?)(?:\s+on\s+the\s+web)?",
            "download_file": r"(?:download|fetch|save|get)\s+(?:the\s+)?(.+?)(?:\s+file|\s+from\s+the\s+internet|\s+online|\s+to\s+my\s+computer)?",
            "system_command": r"(?:perform|execute)?\s*(shutdown|restart|increase volume|decrease volume|mute|lock)(?:\s+my\s+computer|\s+the\s+system|\s+now|\s+command)?",
            "exit": r"(?:exit|stop|quit|close|terminate)\s+(?:the\s+)?(\w+)(?:\s+now)?",
        }
    
        try:
            model, tokenizer, classifier = self.load_model_and_tokenizer()
        except FileNotFoundError as e:
            print(e)
            voice_assistant.speak("Please upload the model directory files.")
    
        print("\nIntent Recognition Results:")
        result = self.process_input(input_text, classifier, label_map, regex_patterns)
        print(f"Intent: {result['intent']}, Entity: {result['entity']}, Confidence: {result['confidence']}")
        print("-" * 50)
        return result