import os
import json

from sentence_transformers import SentenceTransformer

from chunk import ChunkFactory


class AllChunkFactory:

    def __init__(self):

        self.model = SentenceTransformer(

            "sentence-transformers/all-MiniLM-L6-v2"

        )

        self.all_chunks = []


    # --------------------------------------------------
    # Load existing chunks
    # --------------------------------------------------

    def load_existing(

        self,

        input_path="backend/data/chunk_factory/all_chunks.json"

    ):


        if not os.path.exists(input_path):

            print(

                "No existing chunk file found."

            )

            return self


        with open(

            input_path,

            "r",

            encoding="utf-8"

        ) as f:


            self.all_chunks = json.load(f)


        print(

            "Loaded existing chunks:",

            len(self.all_chunks)

        )


        return self


    # --------------------------------------------------
    # Add one input directory
    # --------------------------------------------------

    def add_directory(

        self,

        input_dir,

        source_type

    ):


        chunk_factory = ChunkFactory(

            input_dir=input_dir,

            model=self.model,

            source_type=source_type

        )


        chunks = (

            chunk_factory

            .process()

            .get_chunks()

        )


        self.all_chunks.extend(

            chunks

        )


        return self


    # --------------------------------------------------
    # Add existing chunks manually
    # --------------------------------------------------

    def add_chunks(

        self,

        chunks

    ):


        self.all_chunks.extend(

            chunks

        )


        return self


    # --------------------------------------------------
    # Assign global IDs
    # --------------------------------------------------

    def assign_chunk_ids(self):

        for chunk_id, chunk in enumerate(

            self.all_chunks,

            start=1

        ):


            chunk["chunk_id"] = chunk_id


        return self


    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(

        self,

        output_dir="backend/data/chunk_factory",

        filename="all_chunks.json"

    ):


        os.makedirs(

            output_dir,

            exist_ok=True

        )


        output_path = os.path.join(

            output_dir,

            filename

        )


        with open(

            output_path,

            "w",

            encoding="utf-8"

        ) as f:


            json.dump(

                self.all_chunks,

                f,

                ensure_ascii=False,

                indent=4

            )


        print(

            "Chunks saved successfully to:",

            output_path

        )


        return self


    # --------------------------------------------------
    # Get chunks
    # --------------------------------------------------

    def get_chunks(self):

        return self.all_chunks