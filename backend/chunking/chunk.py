import os
import json

from sentence_transformers import SentenceTransformer


class ChunkFactory:

    def __init__(
        self,
        input_dir,
        model,
        min_words=100,
        max_words=500,
        source_type=None
    ):

        self.input_dir = input_dir

        self.model = model

        self.min_words = min_words

        self.max_words = max_words

        self.source_type = source_type

        self.documents = []

        self.joined_documents = []

        self.chunks = []


    # --------------------------------------------------
    # 1. Load documents
    # --------------------------------------------------

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

                self.documents.append({
                    "source_type": self.source_type,
                    "source": input_path,
                    "article": article_title,
                    "section": section.get("title", "General"),
                    "text": section.get("text", "")
                })
        return self


    # --------------------------------------------------
    # 2. Join short sections
    # --------------------------------------------------

    def join_sections(self):

        joined_documents = []

        i = 0


        while i < len(self.documents):

            current = self.documents[i]


            word_count = len(
                current["text"].split()
            )


            # Section is large enough
            if word_count >= self.min_words:

                joined_documents.append(current)

                i += 1

                continue


            # Section is too small
            if (

                i + 1 < len(self.documents)

                and self.documents[i + 1]["article"]

                == current["article"]

            ):

                next_document = self.documents[i + 1]


                joined_document = {

                    "source_type": current["source_type"],

                    "source": current["source"],

                    "article": current["article"],

                    "section": [

                        current["section"],

                        next_document["section"]

                    ],

                    "text": (

                        current["text"]

                        + "\n\n"

                        + next_document["text"]

                    )

                }


                joined_documents.append(
                    joined_document
                )


                i += 2


            else:

                joined_documents.append(
                    current
                )

                i += 1


        self.joined_documents = joined_documents


        return self


    # --------------------------------------------------
    # 3. Split into chunks
    # --------------------------------------------------

    def split_section(self, document):

        words = document["text"].split()


        chunks = []


        for i in range(

            0,

            len(words),

            self.max_words

        ):


            chunk_words = words[

                i:i + self.max_words

            ]


            chunks.append({

                "source_type": document["source_type"],

                "source": document["source"],

                "article": document["article"],

                "section": document["section"],

                "text": " ".join(chunk_words)

            })


        return chunks


    # --------------------------------------------------
    # 4. Create all chunks
    # --------------------------------------------------

    def create_chunks(self):

        all_chunks = []


        for document in self.joined_documents:

            section_chunks = (

                self.split_section(document)

            )


            all_chunks.extend(
                section_chunks
            )


        self.chunks = all_chunks


        return self


    # --------------------------------------------------
    # 5. Create embeddings
    # --------------------------------------------------

    def create_embeddings(self):

        for chunk in self.chunks:


            embedding = self.model.encode(

                chunk["text"]

            ).tolist()


            chunk["embedding"] = embedding


        return self


    # --------------------------------------------------
    # 6. Get chunks
    # --------------------------------------------------

    def get_chunks(self):

        return self.chunks


    # --------------------------------------------------
    # 7. Run complete pipeline
    # --------------------------------------------------

    def process(self):

        (

            self

            .load_documents()

            .join_sections()

            .create_chunks()

            .create_embeddings()

        )


        return self