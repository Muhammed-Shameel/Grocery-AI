import os
import json

class VectorDatabase():
    def __init__(self, path=None):
        if path is None:
            # Get the directory of the current file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the path to backend/data/chunk_factory/all_chunks.json
            # The structure is backend/database/vector_database.py
            # So ../data/chunk_factory/all_chunks.json
            path = os.path.join(base_dir, '..', 'data', 'chunk_factory', 'all_chunks.json')
        self.chunks = []
        self.path = path
    
    
    def load_data(self):
        with open(self.path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
            

    def save_data(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                self.chunks,
                f,
                indent=4,
                ensure_ascii=False
            )
            
    def add_chunk(self, new_chunk):
        self.chunks.append(new_chunk)
    
    def delete_chunk(self, chunk_id):
        for chunk in self.chunks:
            if chunk_id == chunk["chunk_id"]:
                self.chunks.remove(chunk)
                break

    def count_chunks(self): 
        return len(self.chunks)
    
    def get_chunk(self, chunk_id):
        for chunk in self.chunks:
            if chunk_id == chunk["chunk_id"]:
                return chunk
        else:
            return None
    
    def get_all_chunks(self):
        return self.chunks