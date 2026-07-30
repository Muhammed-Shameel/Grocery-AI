from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

class SemanticChunking():
    def __init__(self, embeddings):
        self.semantic_chunks = []
        self.embeddings = embeddings
        
    def semantic_chunking(self, recursive_sections):

        splitter = SemanticChunker(
            embeddings=self.embeddings
        )

        for section in recursive_sections:

            chunks = splitter.split_text(section["text"])

            for idx, chunk in enumerate(chunks):

                new_chunk = section.copy()

                new_chunk["text"] = chunk
                new_chunk["semantic_chunk_id"] = idx
                new_chunk["total_semantic_chunks"] = len(chunks)

                self.semantic_chunks.append(new_chunk)

        return self
    
    def get_chunks(self):
        return self.semantic_chunks