import json
import urllib.request


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/":
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps({"message": "Используй /USD /EUR и т.д."}).encode()]

    currency = path.strip("/").upper()
    api_url = f"https://api.exchangerate-api.com/v4/latest/{currency}"

    with urllib.request.urlopen(api_url) as response:
        data = response.read()
        status = response.status

    start_response(f"{status} OK", [("Content-Type", "application/json")])
    return [data]

# Для запуска ввести gunicorn app_wsgi:application --bind 0.0.0.0:8000
