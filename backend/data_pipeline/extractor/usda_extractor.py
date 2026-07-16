import os
import requests
from dotenv import load_dotenv


class USDAExtractor:

    SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

    DETAIL_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self):

        load_dotenv()

        self.api_key = os.getenv("USDA_API_KEY")

        if not self.api_key:
            raise ValueError("USDA_API_KEY not found")

    def search_food(self, query, page_size=10):

        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size
        }

        response = requests.get(
            self.SEARCH_URL,
            params=params
        )

        response.raise_for_status()

        return response.json()

    def get_food_details(self, fdc_id):

        params = {
            "api_key": self.api_key
        }

        url = f"{self.DETAIL_URL}/{fdc_id}"

        response = requests.get(
            url,
            params=params
        )

        response.raise_for_status()

        return response.json()