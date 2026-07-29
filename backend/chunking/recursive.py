from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import json

class RecursiveSectionMaker():
    def __init__(
        self,
        input_dir,
        min_words=100,
        max_words=500,
        source_type=None
    ):
        self.input_dir = input_dir
        self.min_words = min_words
        self.max_words = max_words
        self.source_type = source_type
        self.raw_documents = []

        self.recursive_sections  = []


        
        
        
    def load_documents(self):
        for filename in os.listdir(self.input_dir):
            if not filename.endswith(".json"): continue
            input_path = os.path.join(self.input_dir, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Determine structure: List of foods or Dictionary of sections
            if isinstance(data, list):
                # Grocery JSON schema
                article_title = os.path.splitext(filename)[0].capitalize()
                sections = data
            elif isinstance(data, dict):
                # PDF JSON schema (nested or flat)
                if "document" in data and "title" in data["document"]:
                    article_title = data["document"]["title"]
                elif "title" in data:
                    article_title = data["title"]
                else:
                    article_title = os.path.splitext(filename)[0].capitalize()
                sections = data.get("sections", [data]) # Fallback to whole dict if no sections
            else:
                continue

            for section in sections:
                # PROACTIVE FILTER: Only ingest RAG-relevant, non-noise sections
                if not section.get("rag_relevant", True): continue
                if section.get("category") == "noise": continue

                self.raw_documents.append({
                    "source_type": self.source_type,
                    "source": input_path,
                    "article": article_title,
                    "section": section.get("title", "General"),
                    "text": section.get("text", "")
                })
        return self
    
    
    
    
    