import json


class Ingester:

    def __init__(
        self,
        chunk_path,
        embedder,
        chroma_db
    ):
        self.chunk_path = chunk_path
        self.embedder = embedder
        self.chroma_db = chroma_db

        self.chunks = []

    def load_chunks(self):
        """Load semantic chunks from JSON."""

        with open(self.chunk_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        print(f"Loaded {len(self.chunks)} chunks.")

        return self

    def ingest(self):
        """Embed chunks and store them in ChromaDB."""

        ids = []
        documents = []
        metadatas = []

        for chunk in self.chunks:

            article = chunk["article"].replace(" ", "_")
            section = chunk["section"].replace(" ", "_")

            chunk_id = (
                f"{article}_"
                f"{section}_"
                f"{chunk['recursive_chunk_id']}_"
                f"{chunk['semantic_chunk_id']}"
            )

            ids.append(chunk_id)

            documents.append(chunk["text"])

            metadatas.append({
                "article": chunk["article"],
                "section": chunk["section"],
                "source": chunk["source"],
                "source_type": chunk["source_type"],
                "recursive_chunk_id": chunk["recursive_chunk_id"],
                "semantic_chunk_id": chunk["semantic_chunk_id"],
                "total_recursive_chunks": chunk["total_recursive_chunks"],
                "total_semantic_chunks": chunk["total_semantic_chunks"]
            })

        print("Generating embeddings...")

        embeddings = self.embedder.embed_documents(documents)

        print(f"Generated {len(embeddings)} embeddings.")

        print("Uploading to ChromaDB...")

        self.chroma_db.add_documents(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print("Finished ingestion.")

        return self