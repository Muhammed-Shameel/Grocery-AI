import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Words/phrases that signal the user explicitly wants a deeper, structured answer.
# NOTE: narrow factual questions ("how long", "how to store") are intentionally
# NOT here — those should get short, focused answers (concise mode).
_DEEP_SIGNALS = [
    "in detail", "in-depth", "in depth", "deep dive", "full", "comprehensive",
    "everything", "elaborate", "breakdown", "break down", "tell me more",
    "more about", "more details", "thorough", "complete", "explain",
    "compare", "comparison", " versus ", " vs ", "list all", "all the",
    "nutrition facts", "nutritional breakdown", "break it down",
]


class ReasoningAgent:
    """Generates strictly grounded, scannable responses with clear information hierarchy,
    direct answers first, highlighted key values, warning callouts, and clean tables."""

    def __init__(self, llm: Any):
        self.llm = llm

    @staticmethod
    def _wants_deep_answer(question: str) -> bool:
        """Heuristic: does the user explicitly ask for depth/detail?"""
        if not question:
            return False
        q = question.lower()
        return any(sig in q for sig in _DEEP_SIGNALS)

    def generate_answer(self, question: str, context: str, visual_observation: Optional[Dict[str, Any]] = None) -> str:
        """Constructs enhanced prompt enforcing strict data grounding and polished information hierarchy.

        Response depth adapts to the request: concise by default, structured deep-dive
        only when the user explicitly asks for more detail."""

        visual_context_str = ""
        if visual_observation and visual_observation.get("status") == "success":
            visual_context_str = f"""
[Computer Vision Observation — {visual_observation.get('model_version', 'v0.0.1 (trial)')}]
- Detected item: {visual_observation.get('classification')}
- Confidence: {visual_observation.get('confidence')}
- Note: This visual identification is an experimental trial and only recognizes the trained classes (apple, banana, tomato). Treat it as a hint about the food item; still answer ONLY from the retrieved context.
"""
        elif visual_observation and visual_observation.get("status") in ("cv_unavailable", "cv_model_in_progress"):
            visual_context_str = """
[Computer Vision Observation]
- Note: An image was provided, but automatic recognition (experimental trial) is unavailable for this request. Answer from the text question and retrieved context.
"""

        deep = self._wants_deep_answer(question)
        if deep:
            style_guidelines = """
RESPONSE PRESENTATION & INFORMATION HIERARCHY GUIDELINES (DETAILED MODE — user asked for depth):
- DIRECT ANSWER FIRST: Begin immediately with a concise, direct 1-sentence answer or summary answering the user's core question. Avoid repetitive filler preambles (e.g. do NOT say "Based on the provided documents...").
- VISUAL HIERARCHY & SCANNABILITY:
  * Use clear section headings (###) and bold subtitles to group related concepts.
  * HIGHLIGHT KEY VALUES: Always bold important numbers, temperatures, durations, shelf lives, and storage thresholds (e.g. **4°C / 40°F or below**, **2 hours or longer**, **3–5 days**).
  * SAFETY & WARNING CALLOUTS: For food safety, spoilage, or discard rules, format them as Markdown blockquotes:
    > **Food Safety Note:** Discard milk that has been left at room temperature for **2 hours or longer**.
  * COMPARISON / QUANTITATIVE QUESTIONS: Use a clean Markdown table with clear column headers and right-aligned numerical values. Explicitly include measurement bases (e.g. *per 100g*).
  * HOW-TO & PROCEDURAL QUESTIONS: Structure with actionable steps or clear topical sub-sections.
  * Simple definitions: a concise definition, purpose, and key details without unnecessary visual bloat."""
        else:
            style_guidelines = """
RESPONSE PRESENTATION (CONCISE MODE — default):
- Keep it SHORT and focused: a direct 1-3 sentence answer to exactly what was asked.
- Only add a few key facts as at most 2-4 short bullet points if genuinely useful.
- Do NOT use headings, tables, section blocks, or long multi-paragraph breakdowns.
- Bold only the single most important value if any (e.g. a temperature or duration). No filler, no repetition.
- If the user wants a deeper/full breakdown, they will ask for it."""

        prompt = f"""
CRITICAL SYSTEM INSTRUCTION (STRICT GROUNDING & ZERO HALLUCINATION):
1. Answer ONLY using information contained in the retrieved Grocery AI context provided to you below. 
2. Do not use pretrained knowledge, world knowledge, assumptions, memory, or information not present in the supplied context.
3. If the retrieved context does not contain sufficient information to answer the user's question, state clearly that the requested information was not found in the Grocery AI knowledge base.
4. If the question asks multiple things and only part is in the context, answer the supported part and explicitly state what part is unavailable in the knowledge base.
5. Never fill missing information using your own knowledge. Never fabricate citations, numbers, or facts.
6. Match the length of your answer to the scope of the question: answer what was asked, nothing more.
{style_guidelines}

{visual_context_str}

[Retrieved Knowledge Context]
{context}

Question: {question}
Answer:"""

        return self.llm.generate(prompt)
