import chromadb
from sympy import limit


class ChromaDBManager:
    def __init__(
        self,
        db_path: str,
        collection_name: str = "grocery_ai"
    ):
        self.db_path = db_path
        self.collection_name = collection_name

        # Connect to the persistent database
        self.client = chromadb.PersistentClient(path=self.db_path)

        # Create or load the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        
    def count(self):
        return self.collection.count()
    
    def peek(self, limit=5):
        return self.collection.peek(limit=limit)
    
    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas
    ):
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
    def query(
        self,
        query_embedding,
        n_results=5
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
    def delete_collection(self):
        self.client.delete_collection(self.collection_name)