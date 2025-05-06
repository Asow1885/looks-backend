import requests

url = "http://127.0.0.1:5000/ai_optimize_route"

data = {
    "from": "Houston",
    "to": "Atlanta",
    "weather": "clear",
    "traffic": "medium",
    "cargo_type": "electronics"
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())
