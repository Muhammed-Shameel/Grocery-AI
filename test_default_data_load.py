import sys
import os

# Add backend to sys.path to be able to import
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database.vector_database import VectorDatabase

try:
    # Use default
    db = VectorDatabase()
    print(f"Trying to load from: {db.path}")
    db.load_data()
    print(f"Successfully loaded {db.count_chunks()} chunks.")
except Exception as e:
    print(f"Failed to load data from {db.path}: {e}")
