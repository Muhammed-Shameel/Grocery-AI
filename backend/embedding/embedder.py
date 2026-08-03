from langchain_huggingface import HuggingFaceEmbeddings


class Embedder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.model_name = model_name

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name
        )

    def embed_query(self, text: str):
        """Embed a single query."""
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]):
        """Embed multiple documents."""
        return self.embeddings.embed_documents(texts)