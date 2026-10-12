import requests

API_URL = "http://127.0.0.1:8000/ask"
API_KEY = "mysecretkey123"

def ask_employee(question, thread_id="user1"):
    res = requests.post(
        API_URL,
        json={"question": question},  # removed thread_id, old API doesn't need it
        headers={"x-api-key": API_KEY},  # small letters
        timeout=30
    )
    if res.status_code == 200:
        return res.json()["answer"]
    else:
        return f"Error {res.status_code}: {res.text}"

while True:
    q = input("Your question (exit to stop): ")
    if q.lower() == "exit":
        break
    print(ask_employee(q))