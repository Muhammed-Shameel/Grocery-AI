import os
import json
import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    user_agent="GroceryAI/1.0 (muhammedshameel3009@gmail.com)",
    language="en"
)

topics = [
    "milk",
    "banana",
    "apple",
    "orange",
    "mango",
    "pineapple",
    "strawberry",
    "grape",
    "tomato",
    "potato",
    "carrot",
    "spinach",
    "broccoli",
    "rice",
    "wheat",
    "oats",
    "chicken",
    "fish"
]

output_dir = "data_pipeline/raw/wiki"

os.makedirs(output_dir, exist_ok=True)


for topic in topics:

    page = wiki.page(topic)
    
    if not page.exists():
        print("Page Not Fount 404")
        continue

    article = {
        "title":page.title,
        "summary":page.summary,
        "sections":[]
        
    }

    for section in page.sections:
        article["sections"].append({
            "title":section.title,
            "text":section.text
        })
        
    output_path = os.path.join(
        output_dir,
        f"{topic}.json"
    )
    
    with open (output_path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=4)
    
print("Saved Succesffuly")