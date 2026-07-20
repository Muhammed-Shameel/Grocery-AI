from chunking.all_chunk_factory import AllChunkFactory


factory = (

    AllChunkFactory()

    .add_directory(

        input_dir="backend/data_pipeline/clean",

        source_type="cleaned_data"

    )

    .assign_chunk_ids()

    .save()

)