import json
from pathlib import Path

class RawStorage:
    
    def __init__(self, base_directory="data_pipeline/raw/usda"):
        
        self.base_directory = Path(base_directory)
        
        self.base_directory.mkdir(
            parents=True,
            exist_ok=True
        )
        
    def save(self, filename, data):
        
        file_path = self.base_directory / filename
        
        with open(file_path, "w", encoding="utf-8") as file:
            
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )
            
        return file_path