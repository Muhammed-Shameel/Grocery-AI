"""
pdf_text_cleaner.py

Expert structural reconstruction and context-aware content classification.
"""

import re

class PDFTextCleaner:
    def __init__(self, text):
        self.text = text
        self.sections = []

    def _is_technical_noise(self, line):
        stripped = line.strip()
        if len(stripped) < 10: return False
        # Symbols density: very high for formulas/sequences
        symbols = len(re.findall(r"[^a-zA-Z0-9\s]", stripped))
        return (symbols / len(stripped)) > 0.3 or re.search(r"[A-Z]{3,}-[A-Z]{3,}", stripped)

    def _is_heading(self, line):
        s = line.strip()
        if not s or len(s) > 80: return False
        if s[-1] in ".?!": return False # Sentences aren't headings
        # Exclude common table/figure markers
        if any(kw in s.lower() for kw in ['table', 'figure', 'fig.']): return False
        
        is_numbered = bool(re.match(r'^\s*\d+(\.\d+)*\s+[A-Z].*', s))
        is_title = bool(re.match(r'^\s*[A-Z][A-Za-z]+(\s+[A-Z][a-z]+)*\s*$', s))
        is_caps = bool(re.match(r'^\s*[A-Z\s]{5,}\s*$', s))
        
        return (is_numbered or is_title or is_caps) and not self._is_technical_noise(s)

    def _clean_title(self, title):
        return re.sub(r'^\s*\d+(\.\d+)*\s*', '', title).strip()

    def detect_sections(self):
        lines = [l for l in self.text.splitlines() if not self._is_technical_noise(l)]
        if not lines: return self
        
        sections = []
        current_section = {"title": "Introduction", "text": []}
        
        # Lookahead-based heading validation
        for i, line in enumerate(lines):
            is_heading = self._is_heading(line)
            
            # Validation: Heading must not be followed by another heading
            if is_heading:
                next_line = lines[i+1] if i+1 < len(lines) else ""
                if self._is_heading(next_line):
                    is_heading = False # False positive
            
            if is_heading:
                if current_section["text"]:
                    self._finalize_section(current_section)
                current_section = {"title": self._clean_title(line), "text": []}
            else:
                current_section["text"].append(line)
        
        self._finalize_section(current_section)
        return self

    def _finalize_section(self, section):
        body = "\n".join(section["text"]).strip()
        if not body: return # Reject only completely empty sections
        
        cat, relevant, score = self._classify(section['title'], body)
        
        # Consider it clean if it passes basic content relevance
        is_clean = len(body) > 20
        
        self.sections.append({
            "title": section["title"],
            "text": body,
            "category": cat,
            "rag_relevant": relevant,
            "relevance_score": score,
            "quality": {"is_clean": is_clean}
        })

    def _classify(self, title, text):
        t = (title + " " + text).lower()
        # High confidence categorization
        if any(kw in t for kw in ['protein', 'fat', 'lactose', 'mineral', 'vitamins']): return 'food_composition', True, 0.98
        if any(kw in t for kw in ['storage', 'safety', 'pasteur', 'preservation']): return 'food_processing', True, 0.95
        if len(text) < 100: return 'noise', False, 0.1
        return 'general_food_science', True, 0.7

    def get_sections(self):
        return self.sections
