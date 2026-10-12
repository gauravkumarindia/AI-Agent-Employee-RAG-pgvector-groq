import requests
r = requests.post("http://127.0.0.1:8000/ask",
  json={"question":"Who knows Python?"},
  headers={"x-api-key":"mysecretkey123"}
)
print(r.json())