from hybrid import HybridChunker
from langchain_huggingface import HuggingFaceEmbeddings

# Root directory containing ALL cleaned JSON folders
input_dir = r"backend\data_pipeline\clean"

# Where the semantic chunks will be saved
output_dir = r"backend\data\chunk_factory"

# Embedding model (used by SemanticChunker)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

hybrid = HybridChunker(
    input_dir=input_dir,
    output_dir=output_dir,
    embeddings=embeddings,
    chunk_size=1500,
    chunk_overlap=300
)

chunks = hybrid.chunk()

print(f"Generated {len(chunks)} chunks.")