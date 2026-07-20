class ContextSelector:

    def __init__(self, top_chunks, question_analysis):

        self.top_chunks = top_chunks

        self.question_analysis = question_analysis


    def select_top_k(self, chunks, top_k=15):

        return chunks[:top_k]


    def filter_by_score(self, chunks, min_score=0.35):
        """
        Permissive score filtering to ensure relevant context is captured,
        relying on later stages for ranking.
        """
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


    def filter_by_category(self, chunks):
        """Prioritize sections that match the preferred categories from question analysis."""
        preferred = self.question_analysis.preferred_categories
        if not preferred or "general_food_science" in preferred:
            return chunks
        
        filtered = []
        for chunk, score in chunks:
            if chunk.get("category") in preferred:
                filtered.append((chunk, score * 1.2)) # Boost relevant categories
            else:
                filtered.append((chunk, score))
        return sorted(filtered, key=lambda x: x[1], reverse=True)

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
        
        chunks = self.filter_by_category(
            chunks
        )

        return chunks