import os
import voyageai
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:

    def __init__(self):

        self.client = voyageai.Client(
            api_key=os.getenv("VOYAGE_API_KEY")
        )

        self.model = "voyage-4-lite"


    def embed_documents(self, texts):

        result = self.client.embed(
            texts,
            model=self.model,
            input_type="document"
        )

        return result.embeddings


    def embed_query(self, query):

        result = self.client.embed(
            [query],
            model=self.model,
            input_type="query"
        )

        return result.embeddings[0]