import requests
import json

API_URL = "http://localhost:5050/trigger"

TESTS = [
    {
        "name": "No backup - uso normale",
        "data": {
            "token_usage": 800,
            "response_time": 0.4,
            "error_detected": False
        }
    },
    {
        "name": "Trigger backup - token alto",
        "data": {
            "token_usage": 1600,
            "response_time": 0.4,
            "error_detected": False
        }
    },
    {
        "name": "Trigger backup - latenza alta",
        "data": {
            "token_usage": 400,
            "response_time": 3.2,
            "error_detected": False
        }
    },
    {
        "name": "Fallback Claude - crash AI",
        "data": {
            "token_usage": 900,
            "response_time": 0.6,
            "error_detected": True
        }
    }
]


def run_tests():
    for test in TESTS:
        print(f"\n[Test] {test['name']}")
        response = requests.post(API_URL, json=test['data'])
        print("Status:", response.status_code)
        print("Risposta:", json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    run_tests()
