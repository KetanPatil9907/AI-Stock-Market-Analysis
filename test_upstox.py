import requests

TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4OEI5MjYiLCJqdGkiOiI2YWExNTVmYTlmZTc2YzQ4MDQ0NDlkMDYiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlzRXh0ZW5kZWQiOnRydWUsImlhdCI6MTc4ODk1ODIwMiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxODIwNTI3MjAwfQ.oXH6jTii6q7sorUyMWH22-aBKD1rFztvx9TlS5z3J50"



# IPO ID received from the /v2/ipos API
ipo_id = "veegaland-developers-limited-ipo"

url = f"https://api.upstox.com/v2/ipos/{ipo_id}"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

response = requests.get(
    url,
    headers=headers,
    timeout=20
)

print("Status Code:", response.status_code)
print("Response:")
print(response.text)