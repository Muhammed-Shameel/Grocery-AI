import logging
from typing import Optional, List, Dict, Any, Tuple
from agents.security_guardrail import SecurityGuardrail
from agents.vision_agent import VisionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.reasoning_agent import ReasoningAgent

logger = logging.getLogger(__name__)

class Orchestrator:
    """Supervisor agent coordinating security, vision, retrieval, grounding gate, and reasoning."""
    
    def __init__(self, retriever: Any, context_builder: Any, llm: Any):
        self.guardrail = SecurityGuardrail()
        self.vision_agent = VisionAgent()
        self.retrieval_agent = RetrievalAgent(retriever, context_builder)
        self.reasoning_agent = ReasoningAgent(llm)

    def process_request(self, question: str, subject: Optional[str] = None, image_data: Optional[Any] = None, history: Optional[List[dict]] = None) -> Dict[str, Any]:
        # 1. Security & Guardrail Check
        guardrail_result = self.guardrail.validate(question)
        if not guardrail_result["is_safe"]:
            return {
                "question": question,
                "answer": guardrail_result["sanitized_text"],
                "sources": [],
                "visual_observation": None,
                "grounded": False,
                "subject": subject
            }
        
        sanitized_question = guardrail_result["sanitized_text"]

        # 2. Vision Analysis (if image provided)
        visual_obs = self.vision_agent.analyze_image(image_data)
        
        effective_query = sanitized_question
        if visual_obs and visual_obs.classification and visual_obs.classification not in ["pending_cv_implementation", "no_image_provided"]:
            # Anchor retrieval with the CV-detected item so pronoun-style
            # questions like "how long can I store THIS" still retrieve the
            # right subject's knowledge (e.g. "apple").
            if not effective_query or effective_query.strip() == "":
                effective_query = f"Tell me about {visual_obs.classification} storage and nutrition."
            else:
                effective_query = f"{visual_obs.classification}: {sanitized_question}"

        # 2b. If an image was provided but CV could NOT identify it (e.g. torch
        # unavailable on the free-tier host), AND the user only sent a generic
        # "analyze this" placeholder with no real text, then there is nothing
        # meaningful to retrieve. Sending the placeholder through the vector
        # store returns an unrelated match (e.g. a random USDA article) and the
        # LLM answers about the wrong item. Tell the user instead of guessing.
        _placeholder_queries = {
            "analyze this image", "analyse this image", "analyze this product",
            "analyse this product", "analyze this", "analyse this",
            "describe this image", "describe this product", "what is this",
            "what is in this image", "",
        }
        is_placeholder = sanitized_question.strip().lower().rstrip(".") in _placeholder_queries
        cv_failed = bool(image_data) and not (visual_obs and visual_obs.classification)
        if is_placeholder and cv_failed:
            logger.info(
                "Image provided but CV unavailable and no textual query; "
                "skipping retrieval to avoid an unrelated grounded answer."
            )
            return {
                "question": question,
                "answer": (
                    "I received your image, but **image recognition (v0.0.1 trial) "
                    "isn't available on this server** — the vision model runs "
                    "locally, not on the free-tier host, so I can't tell what's in "
                    "the photo from text alone and I won't guess.\n\n"
                    "Try one of these instead:\n"
                    "- **Type the item** in your question (e.g. "
                    "\"How long do apples last?\").\n"
                    "- Run the backend **locally** (where PyTorch + the CV model "
                    "are installed) to use automatic image detection."
                ),
                "sources": [],
                "visual_observation": visual_obs.dict() if visual_obs else None,
                "grounded": False,
                "subject": subject,
            }

        # 3. Retrieval with optional subject filtering
        context, results = self.retrieval_agent.retrieve_and_build_context(effective_query, top_k=5, subject=subject)

        # 4. Strict Grounding Gate: NO EVIDENCE = NO KNOWLEDGE ANSWER
        RELEVANCE_THRESHOLD = 0.20
        has_valid_evidence = False
        if results:
            for chunk, score in results:
                if score >= RELEVANCE_THRESHOLD:
                    has_valid_evidence = True
                    break

        if not has_valid_evidence or not results:
            logger.info("No relevant evidence found above threshold. Refusing general knowledge answer.")
            # If CV identified something, acknowledge it warmly instead of a
            # cold refusal — but still make clear the knowledge base has no info.
            if visual_obs and visual_obs.status == "success" and visual_obs.classification:
                confidence_pct = round((visual_obs.confidence or 0.0) * 100)
                no_evidence_answer = (
                    f"That looks like **{visual_obs.classification}** "
                    f"(detected with about **{confidence_pct}%** confidence), but I "
                    f"couldn't find any information about it in the Grocery AI "
                    f"knowledge base yet."
                )
            else:
                no_evidence_answer = (
                    "I couldn't find information about that in the Grocery AI knowledge base."
                )
            return {
                "question": question,
                "answer": no_evidence_answer,
                "sources": [],
                "visual_observation": visual_obs.dict() if visual_obs and visual_obs.status != "no_image_provided" else None,
                "grounded": False,
                "subject": subject
            }

        # 5. Reasoning / Answer Generation
        answer = self.reasoning_agent.generate_answer(sanitized_question, context, visual_obs.dict() if visual_obs else None)

        # 6. Format Sources
        sources = [
            {
                "title": chunk.get("article"),
                "article": chunk.get("article"),
                "section": chunk.get("section"),
                "source": chunk.get("source"),
                "score": score,
                "category": chunk.get("category", "General"),
                "quality": chunk.get("quality", {"is_clean": True})
            }
            for chunk, score in results
        ]

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "visual_observation": visual_obs.dict() if visual_obs and visual_obs.status != "no_image_provided" else None,
            "grounded": True,
            "subject": subject
        }
