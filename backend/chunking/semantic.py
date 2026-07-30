from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

class SemanticChunking():
    def __init__(self, sections, embeddings):
        self.sections = sections
        self.semantic_chunks = []
        self.embeddings = embeddings
    def semantic_chunking(self):
        splitter = SemanticChunker(self.embeddings)
        for section in self.sections:
            chunks = splitter.split_text(section["text"])
            for chunk in chunks:
                new_chunk = section.copy()
                new_chunk["text"] = chunk
                self.semantic_chunks.append(new_chunk)
        return self
    
    def get_chunk(self):
        return self.semantic_chunks