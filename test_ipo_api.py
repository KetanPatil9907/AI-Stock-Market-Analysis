import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IPO_API_KEY")

print("API key loaded:", bool(API_KEY))

url = "https://finapi.upvaly.com/api/ipo"

headers = {
    "X-API-Key": API_KEY
}

response = requests.get(
    url,
    headers=headers,
    timeout=20
)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)