from typing import List, Tuple, Dict, Any

class ContextBuilder:
    """Builds a formatted context string from retrieved chunks."""
    
    @staticmethod
    def build(retrieved_results: List[Tuple[Dict[str, Any], float]]) -> str:
        """Builds a single formatted context string."""
        if not retrieved_results:
            return "No relevant context found."
            
        context_parts = ["--------------------------------\nContext\n"]
        
        for chunk, score in retrieved_results:
            source = chunk.get("source", "Unknown")
            section = chunk.get("section", "General")
            text = chunk.get("text", "")
            
            context_parts.append(f"Source: {source}\nSection: {section}\nText: {text}\n")
            
        context_parts.append("--------------------------------")
        return "\n".join(context_parts)
