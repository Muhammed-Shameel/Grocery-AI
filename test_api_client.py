import requests
import json

url = 'http://127.0.0.1:8000/ask'
data = {'question': 'What is the protein content in an egg?'}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
