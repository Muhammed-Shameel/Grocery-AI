"""
chunker.py

Orchestrates the chunking pipeline to process both research and wiki 
cleaned data, and saves them to the centralized chunk factory.
"""

from all_chunk_factory import AllChunkFactory

def main():
    # Initialize and load existing
    factory = AllChunkFactory().load_existing()

    # Process grocery data
    factory.add_directory(
        input_dir="backend/data_pipeline/clean/grocery_unified",
        source_type="grocery"
    )

    # Process research data
    factory.add_directory(
        input_dir="backend/data_pipeline/clean/research",
        source_type="research"
    )

    # Process wiki data
    factory.add_directory(
        input_dir="backend/data_pipeline/clean/wiki",
        source_type="wiki"
    )
    factory.assign_chunk_ids().save()

if __name__ == "__main__":
    main()
