from all_chunk_factory import AllChunkFactory


factory = (

    AllChunkFactory()

    .load_existing()

    .add_directory(

        input_dir="backend/data_pipeline/clean/   ",

        source_type=""

    )

    .assign_chunk_ids()

    .save()

)