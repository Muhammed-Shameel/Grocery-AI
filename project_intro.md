# Grocery AI Learning Roadmap

## 🎯 Final Goal

Build a **Grocery AI Assistant** that:

- Collects knowledge from trusted sources.
- Stores structured data in SQL.
- Stores unstructured knowledge in a vector database.
- Uses Retrieval-Augmented Generation (RAG).
- Uses a Large Language Model (LLM).
- Exposes everything through FastAPI.

---

# Phase 0 — Foundations *(Current Phase)*

## Goal

Understand what a RAG system actually is.

## Learn

- What is RAG?
- Why not send the whole document to an LLM?
- Structured vs Unstructured Data
- Why chunking exists
- What is retrieval?

## Notebook Questions

- Why do we need RAG?
- Why can't an LLM memorize everything?
- What problems does chunking solve?

---

# Phase 1 — Data Engineering

## Goal

Prepare high-quality knowledge.

## Learn

- Data collection
- Trusted sources
- Data cleaning
- Document analysis
- Document structure
- Metadata

## Build Yourself

- [ ] Cleaning
- [ ] Document loader
- [ ] Metadata generation

## Compare Later

- Document loaders from popular RAG libraries

---

# Phase 2 — Chunking

## Goal

Convert documents into meaningful pieces.

## Learn

- Fixed-size chunking
- Sentence chunking
- Paragraph chunking
- Semantic chunking
- Chunk overlap
- Chunk size trade-offs

## Build Yourself

- [ ] Fixed-size chunker
- [ ] Paragraph chunker
- [ ] Semantic chunker

## Compare Later

Compare your implementation with an existing semantic chunker.

Evaluate:

- Number of chunks
- Chunk quality
- Retrieval accuracy

---

# Phase 3 — NLP Foundations

## Goal

Understand how computers read text.

```
Characters
      ↓
Words
      ↓
Tokens
      ↓
Token IDs
```

## Learn

- Tokenization
- Vocabulary
- Subwords
- Byte Pair Encoding (BPE)
- WordPiece
- SentencePiece

## Build Yourself

- [ ] Basic tokenizer
- [ ] Word tokenizer
- [ ] Vocabulary builder

## Compare Later

- Hugging Face Tokenizers
- tiktoken

---

# Phase 4 — Mathematics ⭐

> This is the most important phase.

## Learn

### Linear Algebra

- Scalars
- Vectors
- Dimensions
- Vector spaces

### Equations

#### Vector Magnitude (L2 Norm)

$$
\|A\|=\sqrt{\sum_{i=1}^{n}A_i^2}
$$

#### Dot Product

$$
A\cdot B=\sum_{i=1}^{n}A_iB_i
$$

#### Cosine Similarity

$$
\cos(\theta)=
\frac{A\cdot B}
{\|A\|\|B\|}
$$

### Distance Metrics

- Euclidean Distance
- Manhattan Distance
- Cosine Distance

## Build Yourself

- [ ] Dot Product
- [ ] Vector Magnitude
- [ ] Cosine Similarity
- [ ] Top-K Retrieval

> **No libraries.**

---

# Phase 5 — Embeddings

## Goal

Understand semantic meaning.

## Learn

- What is an embedding?
- Why embeddings work
- Dense vs Sparse vectors
- Semantic similarity

## Important

We **DO NOT** build an embedding model.

### Why?

Training requires:

- Massive datasets
- GPUs
- Transformer architectures
- Contrastive learning

Instead, we will use a **pretrained embedding model**.

## Build Yourself

- [ ] Store embeddings
- [ ] Compare embeddings
- [ ] Visualize embeddings *(optional)*

---

# Phase 6 — Vector Database

## Goal

Build a simple vector database yourself.

```
Chunk
   ↓
Embedding
   ↓
Store
   ↓
Retrieve
```

## Build Yourself

Version 1

- Python List

Version 2

- Dictionary

Version 3

- Optimized structure

## Compare Later

- FAISS
- ChromaDB
- Pinecone

---

# Phase 7 — Retrieval

## Goal

Build your own search engine.

```
Query
   ↓
Embedding
   ↓
Similarity Calculation
   ↓
Ranking
   ↓
Top-K
   ↓
Relevant Chunks
```

## Algorithms

- Cosine Similarity
- Sorting
- Top-K Retrieval

## Compare Later

- Vector database retrieval

---

# Phase 8 — Prompt Engineering

## Goal

Construct effective prompts.

## Learn

- Prompt structure
- Context
- Instructions
- Questions

## Experiment

- Different prompts
- Different K values
- Hallucinations

---

# Phase 9 — LLM

## Goal

Generate answers.

## Learn

- Context Window
- Temperature
- Hallucinations
- Prompt Following

## Use

- Pretrained LLM

> No model training.

---

# Phase 10 — Backend

## Learn

- FastAPI
- API Endpoints
- Request / Response
- Validation
- Database connection
- Complete RAG pipeline

---

# Phase 11 — SQL

## Learn

- Database Normalization
- Tables
- Relationships
- Indexes

## Tables

- Products
- Nutrition
- Categories
- Brands
- Prices

---

# Phase 12 — Production Grocery AI

Combine everything.

```
User Question
      ↓
FastAPI
      ↓
Retriever
      ↓
Vector Search
      ↓
SQL Search
      ↓
Prompt Builder
      ↓
LLM
      ↓
Answer
```

---

# Mathematics Checklist

## Linear Algebra

- [ ] Vector
- [ ] Vector Magnitude (L2 Norm)
- [ ] Dot Product
- [ ] Cosine Similarity
- [ ] Euclidean Distance
- [ ] Manhattan Distance
- [ ] Matrix Multiplication (basic intuition)

---

## Information Retrieval

- [ ] Term Frequency (TF)
- [ ] Document Frequency (DF)
- [ ] Inverse Document Frequency (IDF)
- [ ] TF-IDF
- [ ] Sparse vs Dense Vectors

---

## NLP

- [ ] Tokenization
- [ ] Vocabulary
- [ ] Byte Pair Encoding (BPE)
- [ ] WordPiece
- [ ] SentencePiece
- [ ] Embeddings
- [ ] Context Windows

---

# Development Philosophy

| Component | Build Ourselves | Compare Later |
|------------|:---------------:|:-------------:|
| Data Collection | ✅ | - |
| Data Cleaning | ✅ | - |
| Document Loader | ✅ | ✅ |
| Metadata Generation | ✅ | - |
| Chunking | ✅ | ✅ |
| Basic Tokenizer | ✅ | ✅ |
| Vector Mathematics | ✅ | - |
| Cosine Similarity | ✅ | - |
| Vector Store | ✅ | ✅ |
| Retriever | ✅ | ✅ |
| Prompt Builder | ✅ | - |
| SQL Schema | ✅ | - |
| FastAPI | ✅ | - |
| Embedding Model | ❌ | ✅ |
| LLM | ❌ | ✅ |
| Production Vector Database | ❌ | ✅ |

---

# Learning Philosophy

For every topic, answer these four questions in your notebook:

1. **What is it?**
2. **Why do we need it?**
3. **How does it work mathematically?**
4. **How can I implement it myself?**

Only after building it ourselves will we compare it with production-grade libraries and frameworks.