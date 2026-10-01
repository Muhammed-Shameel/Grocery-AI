import os
import voyageai
from dotenv import load_dotenv

load_dotenv()


class EmbeddingService:

    def __init__(self):

        # voyage-3.5+ / voyage-4 models live on the new API endpoint,
        # not the legacy one the SDK defaults to.
        self.client = voyageai.Client(
            api_key=os.getenv("VOYAGE_API_KEY"),
            base_url="https://api.voyageai.com/v1"
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