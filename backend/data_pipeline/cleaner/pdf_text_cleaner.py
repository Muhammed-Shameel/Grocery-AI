import re


class PDFTextCleaner:

    def __init__(self, text):

        self.text = text

        self.sections = []


    # ==================================================
    # 1. EXTRACT ARTICLE CONTENT
    # ==================================================

    def extract_article_content(self):

        # ------------------------------------------
        # Find Abstract
        # ------------------------------------------

        abstract_match = re.search(

            r"\babstract\b\s*:?",

            self.text,

            flags=re.IGNORECASE

        )


        if abstract_match is None:

            raise ValueError(

                "Abstract section not found"

            )


        # Keep everything from Abstract onward

        self.text = self.text[

            abstract_match.start():

        ]


        # ------------------------------------------
        # Remove References section
        # ------------------------------------------

        references_match = re.search(

            r"(?m)^\s*references\s*$",

            self.text,

            flags=re.IGNORECASE

        )


        if references_match is not None:

            self.text = self.text[

                :references_match.start()

            ]


        return self


    # ==================================================
    # 2. REMOVE PAGE/JOURNAL ARTIFACTS
    # ==================================================

    def remove_page_artifacts(self):

        # ------------------------------------------
        # Page numbers
        #
        # Example:
        #
        # 3 of 12
        # ------------------------------------------

        self.text = re.sub(

            r"\b\d+\s+of\s+\d+\b",

            "",

            self.text,

            flags=re.IGNORECASE

        )


        # ------------------------------------------
        # Journal metadata
        #
        # Example:
        #
        # Nutrients 2022, 14, 2904
        # ------------------------------------------

        self.text = re.sub(

            r"\b[A-Z][A-Za-z]+\s+\d{4},\s+\d+,\s+\d+\b",

            "",

            self.text

        )


        # ------------------------------------------
        # Normalize PDF ligatures
        # ------------------------------------------

        ligatures = {

            "ﬁ": "fi",

            "ﬂ": "fl",

            "ﬀ": "ff",

            "ﬃ": "ffi",

            "ﬄ": "ffl",

        }


        for old, new in ligatures.items():

            self.text = self.text.replace(

                old,

                new

            )


        return self


    # ==================================================
    # 3. CHECK WHETHER A LINE IS A VALID SECTION HEADING
    # ==================================================

    def is_valid_section_heading(self, line):

        line = line.strip()


        # ------------------------------------------
        # Abstract
        # ------------------------------------------

        if re.match(
            r"^abstract\s*:?",
            line,
            flags=re.IGNORECASE
        ):

            return True


        # ------------------------------------------
        # Only top-level numbered sections
        #
        # Required format:
        #
        # 1. Introduction
        # 2. Methods
        # 3. Results
        #
        # ------------------------------------------

        match = re.match(

            r"^(\d+)\.\s+(.+)$",

            line

        )


        if match is None:

            return False


        title = match.group(2).strip()


        # ------------------------------------------
        # Reject anything that looks like a decimal
        # or measurement/table fragment
        # ------------------------------------------

        if re.match(

            r"^\d+(?:\.\d+)?\s*",

            title

        ):

            return False


        # ------------------------------------------
        # Require a reasonable title
        # ------------------------------------------

        words = title.split()


        if len(words) < 2:

            return False


        # ------------------------------------------
        # Reject incomplete fragments
        # ------------------------------------------

        incomplete_endings = {

            "of",
            "with",
            "for",
            "and",
            "or",
            "a",
            "an",
            "the",
            "to",
            "vs",
            "as",
            "in",

        }


        if words[-1].lower() in incomplete_endings:

            return False


        # ------------------------------------------
        # Require actual alphabetic content
        # ------------------------------------------

        if len(re.findall(r"[A-Za-z]", title)) < 5:

            return False


        return True


    # ==================================================
    # 4. DETECT SECTIONS
    # ==================================================

    def detect_sections(self):

        lines = self.text.splitlines()


        sections = []


        current_section = None

        current_text = []


        for line in lines:

            line = line.strip()


            if not line:

                continue


            # ------------------------------------------
            # Use the validation method
            # ------------------------------------------

            if self.is_valid_section_heading(line):


                # Save previous section

                if current_section is not None:

                    sections.append({

                        "title": current_section,

                        "text": "\n".join(

                            current_text

                        )

                    })


                # Start new section

                current_section = line

                current_text = []


            else:

                current_text.append(line)


        # ------------------------------------------
        # Save final section
        # ------------------------------------------

        if current_section is not None:

            sections.append({

                "title": current_section,

                "text": "\n".join(

                    current_text

                )

            })


        self.sections = sections


        return self


    # ==================================================
    # 5. CLEAN SECTION TEXT
    # ==================================================

    def clean_section_text(self, text):


        # ------------------------------------------
        # Remove page numbers
        # ------------------------------------------

        text = re.sub(

            r"\b\d+\s+of\s+\d+\b",

            "",

            text,

            flags=re.IGNORECASE

        )


        # ------------------------------------------
        # Remove citation markers
        #
        # [40]
        # [1-4]
        # [1,2,3]
        # ------------------------------------------

        text = re.sub(

            r"\[\s*\d+(?:\s*[-–,]\s*\d+)*\s*\]",

            "",

            text

        )


        # ------------------------------------------
        # Remove figure/table references
        #
        # Figure 1
        # Fig. 2A
        # Table 3
        # ------------------------------------------

        text = re.sub(

            r"\b(?:figure|fig\.?|table)\s+\d+[A-Za-z]?\b",

            "",

            text,

            flags=re.IGNORECASE

        )


        # ------------------------------------------
        # Remove URLs
        # ------------------------------------------

        text = re.sub(

            r"https?://\S+",

            "",

            text

        )


        # ------------------------------------------
        # Remove journal metadata
        # ------------------------------------------

        text = re.sub(

            r"\b[A-Z][A-Za-z]+\s+\d{4},\s+\d+,\s+\d+\b",

            "",

            text

        )


        # ------------------------------------------
        # Fix hyphenated words split by PDF lines
        #
        # high-
        # quality
        #
        # becomes:
        #
        # high-quality
        # ------------------------------------------

        text = re.sub(

            r"-\s*\n\s*",

            "",

            text

        )


        # ------------------------------------------
        # Replace remaining line breaks with spaces
        # ------------------------------------------

        text = re.sub(

            r"\s*\n\s*",

            " ",

            text

        )


        # ------------------------------------------
        # Remove repeated spaces
        # ------------------------------------------

        text = re.sub(

            r"\s+",

            " ",

            text

        )


        return text.strip()


    # ==================================================
    # 6. CLEAN ALL SECTIONS
    # ==================================================

    def clean_sections(self):

        cleaned_sections = []


        for section in self.sections:


            cleaned_text = self.clean_section_text(

                section["text"]

            )


            # ------------------------------------------
            # Remove empty sections
            # ------------------------------------------

            if not cleaned_text:

                continue


            cleaned_sections.append({

                "title": section["title"],

                "text": cleaned_text

            })


        self.sections = cleaned_sections


        return self


    # ==================================================
    # 7. RETURN SECTIONS
    # ==================================================

    def get_sections(self):

        return self.sections