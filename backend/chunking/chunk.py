import os
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

input_dir = "data_pipeline/clean/wiki"

documents = []

for filename in os.listdir(input_dir):
    
    if not filename.endswith(".json"):
        continue
    
    input_path = os.path.join(input_dir, filename)
    
    with open(input_path, "r", encoding="utf-8") as f:
        article = json.load(f)
        
    article_title = article["title"]
    
    for section in article["sections"]:
        
        documents.append({
            "article": article_title,
            "section": section["title"],
            "text": section["text"]
        })
        
        
        
def join_sections(documents, min_words=100):

    joined_documents = []

    i = 0

    while i < len(documents):

        current = documents[i]

        word_count = len(current["text"].split())

        if word_count >= min_words:

            joined_documents.append(current)

            i += 1

        else:

            if (
                i + 1 < len(documents)
                and documents[i + 1]["article"] == current["article"]
            ):

                next_document = documents[i + 1]

                joined_document = {
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

                joined_documents.append(joined_document)

                i += 2

            else:

                joined_documents.append(current)

                i += 1

    return joined_documents


def split_section(document, max_words=500):

    words = document["text"].split()

    chunks = []

    for i in range(0, len(words), max_words):

        chunk_words = words[i:i + max_words]

        chunks.append({
            "article": document["article"],
            "section": document["section"],
            "text": " ".join(chunk_words)
        })

    return chunks


joined_documents = join_sections(documents)

all_chunks = []

for document in joined_documents:

    section_chunks = split_section(document)

    all_chunks.extend(section_chunks)

for chunk in all_chunks:

    embedding = model.encode(
        chunk["text"]
    ).tolist()

    chunk["embedding"] = embedding

for chunk_id, chunk in enumerate(all_chunks, start=1):
    chunk["chunk_id"] = chunk_id

# Save chunks with embeddings
output_path = "data/processed/wiki_chunks.json"

with open(output_path, "w", encoding="utf-8") as f:

    json.dump(
        all_chunks,
        f,
        ensure_ascii=False,
        indent=4
    )


print("Embeddings created and saved successfully.")
print("Total chunks:", len(all_chunks))