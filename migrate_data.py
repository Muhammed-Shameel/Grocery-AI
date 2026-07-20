import json
import os

def migrate_grocery_json(input_path, output_dir):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Map old categories to new schema structure
    for item in data:
        # Create a unified document structure per item
        unified_doc = {
            "document": {
                "title": item.get("title", "Unknown"),
                "source": "grocery.json",
                "source_type": "grocery"
            },
            "sections": [
                {
                    "section_id": f"sec_{item.get('title', 'item').replace(' ', '_')}",
                    "title": item.get("title", "General"),
                    "text": item.get("text", ""),
                    "category": item.get("category", "general_food_science"),
                    "rag_relevant": True,
                    "relevance_score": 0.95,
                    "quality": {"is_clean": True}
                }
            ]
        }
        
        # Save as individual file to be processed by chunker
        output_filename = f"{item.get('title', 'item').replace(' ', '_').lower()}.json"
        with open(os.path.join(output_dir, output_filename), 'w', encoding='utf-8') as f:
            json.dump(unified_doc, f, indent=4, ensure_ascii=False)
    
    print(f"Migrated {len(data)} items to {output_dir}")

# Execute migration
migrate_grocery_json(
    'backend/data_pipeline/clean/T_Data/grocery.json',
    'backend/data_pipeline/clean/grocery_unified'
)
