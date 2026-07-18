import re

class QuestionUnderstanding():
    def __init__(self, question: str):
        self.org_question = question
        self.normalised_question = question
    
    def question_normaliser(self):
        question = self.org_question.strip()
        question = question.lower()
        question = re.sub(r"\s+", " ", question)
        self.normalised_question = question
        return self
    
    def detect_intent(self):
        nutrient_keywords = ["protein", "calorie", "calories", "vitamin", "mineral", "nutrient", "fat", "carbohydrate"] 
        storage_keywords = ["store", "storage","refrigerator","fridge", "shelf life", "keep"]
        safety_keywords = ["safe", "unsafe", "expired", "spoil", "spoiled", "dangerous"]

        question = self.normalised_question
        
        detected_intents = []
        words = question.split()
        
        for word in words:

            if word in nutrient_keywords and "nutrient" not in detected_intents:
                detected_intents.append("nutrient")

            if word in storage_keywords and "storage" not in detected_intents:
                detected_intents.append("storage")

            if word in safety_keywords and "safety" not in detected_intents:
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

        intents = self.detect_intent()

        attributes = self.extract_attributes()

        entities = self.extract_entity()

        operation = self.determine_operation()

        retrieval_terms = (
            entities
            + attributes
            + intents
        )

        retrieval_query = " ".join(
            retrieval_terms
        )

        return retrieval_query
    
    def calculate_confidence(self):

        intents = self.detect_intent()
        attributes = self.extract_attributes()
        entities = self.extract_entity()
        operations = self.determine_operation()

        confidence = 0

        if intents and intents != ["general"]:
            confidence += 0.25

        if attributes:
            confidence += 0.25

        if entities:
            confidence += 0.25

        if operations and operations != ["general"]:
            confidence += 0.25

        return confidence
    def analyze(self):

        self.question_normaliser()

        intents = self.detect_intent()

        attributes = self.extract_attributes()

        entities = self.extract_entity()

        operations = self.determine_operation()

        retrieval_query = self.build_retrieval_query()

        confidence = self.calculate_confidence()

        return {
            "original_question": self.org_question,
            "normalised_question": self.normalised_question,
            "intents": intents,
            "attributes": attributes,
            "entities": entities,
            "operations": operations,
            "retrieval_query": retrieval_query,
            "confidence": confidence
        }
    
