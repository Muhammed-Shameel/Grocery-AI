import re

class QuestionUnderstanding:

    def __init__(
        self,
        question: str,
        llm_analyzer=None
    ):

        self.org_question = question
        self.normalised_question = question

        self.llm_analyzer = llm_analyzer

        self.intents = []
        self.attributes = []
        self.entities = []
        self.operations = []

        self.retrieval_query = ""
        self.confidence = 0

        self.analysis_source = "rule_based"

    def question_normaliser(self):

        question = self.org_question.strip()
        question = question.lower()
        question = re.sub(r"\s+", " ", question)

        self.normalised_question = question

        return self


    def detect_intent(self):

        nutrient_keywords = [
            "protein",
            "calorie",
            "calories",
            "vitamin",
            "mineral",
            "nutrient",
            "fat",
            "carbohydrate"
        ]

        storage_keywords = [
            "store",
            "storage",
            "refrigerator",
            "fridge",
            "shelf life",
            "keep"
        ]

        safety_keywords = [
            "safe",
            "unsafe",
            "expired",
            "spoil",
            "spoiled",
            "dangerous"
        ]

        question = self.normalised_question

        detected_intents = []

        words = question.split()

        for word in words:

            if (
                word in nutrient_keywords
                and "nutrient" not in detected_intents
            ):
                detected_intents.append("nutrient")

            if (
                word in storage_keywords
                and "storage" not in detected_intents
            ):
                detected_intents.append("storage")

            if (
                word in safety_keywords
                and "safety" not in detected_intents
            ):
                detected_intents.append("safety")

        if not detected_intents:

            return ["general"]

        return detected_intents
    
    def extract_attributes(self):
        attribute_keywords = [
            # Nutrition
            "protein",
            "calorie",
            "calories",
            "fat",
            "carbohydrate",
            "carbs",
            "fiber",
            "sugar",
            "sodium",
            "vitamin",
            "vitamins",
            "mineral",
            "minerals",
            "nutrient",
            "nutrients",
            "cholesterol",

            # Storage
            "shelf life",
            "storage",
            "temperature",
            "refrigeration",
            "freezing",
            "frozen",
            "freshness",

            # Safety / Quality
            "safety",
            "expiration",
            "expiry",
            "spoilage",
            "contamination",
            "quality",

            # Preparation
            "cooking",
            "preparation",
            "boiling",
            "frying",
            "baking",

            # Physical characteristics
            "weight",
            "size",
            "color",
            "texture",
            "taste",
            "smell",

            # General product information
            "ingredients",
            "benefits",
            "uses",
            "types",
            "varieties"
        ]
        attributes = []
        question = self.normalised_question
        words = question.split()
        for word in words:
            if word in attribute_keywords:
                attributes.append(word)
        return attributes
                
    def extract_entity(self):
        entity_keywords = [

            # Eggs
            "egg",
            "eggs",
            "egg white",
            "egg whites",
            "egg yolk",
            "egg yolks",

            # Dairy
            "milk",
            "cheese",
            "yogurt",
            "curd",
            "butter",
            "cream",

            # Meat
            "chicken",
            "beef",
            "mutton",
            "lamb",
            "pork",

            # Fish and seafood
            "fish",
            "salmon",
            "tuna",
            "prawn",
            "prawns",
            "shrimp",

            # Fruits
            "apple",
            "banana",
            "orange",
            "mango",
            "grape",
            "grapes",
            "strawberry",
            "strawberries",
            "watermelon",
            "pineapple",

            # Vegetables
            "potato",
            "potatoes",
            "tomato",
            "tomatoes",
            "onion",
            "onions",
            "carrot",
            "carrots",
            "spinach",
            "broccoli",
            "cabbage",

            # Grains and staples
            "rice",
            "wheat",
            "flour",
            "bread",
            "pasta",
            "oats",

            # Legumes
            "beans",
            "lentils",
            "chickpeas",
            "peas",

            # Nuts and seeds
            "almond",
            "almonds",
            "peanut",
            "peanuts",
            "cashew",
            "cashews",
            "walnut",
            "walnuts",

            # Oils and fats
            "oil",
            "olive oil",
            "coconut oil",
            "vegetable oil",

            # General grocery categories
            "food",
            "fruit",
            "fruits",
            "vegetable",
            "vegetables",
            "meat",
            "dairy",
            "seafood"
        ]
        question = self.normalised_question
        entities = []
        for phrase in entity_keywords:
            if phrase in question:
                if phrase not in entities:
                    entities.append(phrase)
        return entities
    def determine_operation(self):

        lookup_phrases = [
            "what is",
            "what are",
            "how much",
            "how many",
            "how long",
            "where",
            "when",
            "which"
        ]

        comparison_phrases = [
            "compare",
            "comparison",
            "difference",
            "differences",
            "versus",
            "vs",
            "better",
            "worse",
            "more than",
            "less than",
            "higher than",
            "lower than",
            "similar",
            "different"
        ]

        instruction_phrases = [
            "how to",
            "how do i",
            "how should i",
            "what is the best way",
            "steps",
            "method",
            "prepare",
            "cook",
            "store",
            "keep"
        ]

        explanation_phrases = [
            "why",
            "explain",
            "reason",
            "how does",
            "what causes",
            "meaning",
            "means"
        ]

        safety_phrases = [
            "is it safe",
            "safe to eat",
            "can i eat",
            "dangerous",
            "unsafe",
            "expired",
            "spoiled",
            "spoilt",
            "bad",
            "contaminated"
        ]

        question = self.normalised_question

        operations = []

        if any(
            phrase in question
            for phrase in lookup_phrases
        ):
            operations.append("lookup")

        if any(
            phrase in question
            for phrase in comparison_phrases
        ):
            operations.append("comparison")

        if any(
            phrase in question
            for phrase in instruction_phrases
        ):
            operations.append("instruction")

        if any(
            phrase in question
            for phrase in explanation_phrases
        ):
            operations.append("explanation")

        if any(
            phrase in question
            for phrase in safety_phrases
        ):
            operations.append("safety")

        if not operations:
            return ["general"]

        return operations
    
    def build_retrieval_query(self):

        retrieval_terms = (
            self.entities
            + self.attributes
            + self.intents
        )

        self.retrieval_query = " ".join(
            retrieval_terms
        )

        return self.retrieval_query
    
    def calculate_confidence(self):

        confidence = 0

        if (
            self.intents
            and self.intents != ["general"]
        ):
            confidence += 0.25

        if self.attributes:
            confidence += 0.25

        if self.entities:
            confidence += 0.25

        if (
            self.operations
            and self.operations != ["general"]
        ):
            confidence += 0.25

        return confidence
    
    def analyze(self):

        # 1. Normalize
        self.question_normaliser()

        # 2. Rule-based analysis
        self.intents = self.detect_intent()

        self.attributes = (
            self.extract_attributes()
        )

        self.entities = (
            self.extract_entity()
        )

        self.operations = (
            self.determine_operation()
        )

        # 3. Calculate rule-based confidence
        self.confidence = (
            self.calculate_confidence()
        )

        # 4. Use LLM only if analysis is uncertain
        if self.confidence < 0.5:

            if self.llm_analyzer is not None:

                llm_analysis = (
                    self.llm_analyzer.analyze(
                        self.normalised_question
                    )
                )

                self.intents = (
                    llm_analysis.get(
                        "intents",
                        self.intents
                    )
                )

                self.attributes = (
                    llm_analysis.get(
                        "attributes",
                        self.attributes
                    )
                )

                self.entities = (
                    llm_analysis.get(
                        "entities",
                        self.entities
                    )
                )

                self.operations = (
                    llm_analysis.get(
                        "operations",
                        self.operations
                    )
                )

                self.analysis_source = "llm"

        # 5. Build final retrieval query
        self.retrieval_query = (
            self.build_retrieval_query()
        )

        return self
