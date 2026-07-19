class ContextSelector:

    def __init__(self, top_chunks, question_analysis):

        self.top_chunks = top_chunks

        self.question_analysis = question_analysis


    def select_top_k(self, chunks, top_k=7):

        return chunks[:top_k]


    def filter_by_score(self, chunks, min_score=0.62):

        filtered_chunks = []

        for chunk, score in chunks:

            if score >= min_score:

                filtered_chunks.append(
                    (chunk, score)
                )

        return filtered_chunks


    def filter_by_entities(self, chunks):

        filtered_chunks_by_entity = []

        entities = (
            self.question_analysis.extract_entity()
        )

        for chunk, score in chunks:

            chunk_text = chunk["text"].lower()

            for entity in entities:

                if entity.lower() in chunk_text:

                    filtered_chunks_by_entity.append(
                        (chunk, score)
                    )

                    break

        return filtered_chunks_by_entity


    def filter_by_attributes(self, chunks):

        filtered_chunks_by_attributes = []

        attributes = (
            self.question_analysis.extract_attributes()
        )

        for chunk, score in chunks:

            chunk_text = chunk["text"].lower()

            for attribute in attributes:

                if attribute.lower() in chunk_text:

                    filtered_chunks_by_attributes.append(
                        (chunk, score)
                    )

                    break

        return filtered_chunks_by_attributes


    def select_context(self):

        chunks = self.select_top_k(
            self.top_chunks
        )

        chunks = self.filter_by_score(
            chunks
        )

        chunks = self.filter_by_entities(
            chunks
        )

        chunks = self.filter_by_attributes(
            chunks
        )

        return chunks