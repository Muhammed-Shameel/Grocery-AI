import requests
from bs4 import BeautifulSoup

url = "https://www.mdpi.com/2072-6643/14/14/2904"

response = requests.get(url)

print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

print(soup.title.text)