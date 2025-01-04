import requests

url = "http://127.0.0.1:5000/forms"
data = {
    "name": "Sample Form 2",
    "fields": [
        {
            "name": "question1",
            "label": "What is your name?",
            "type": "short text"
        },
        {
            "name": "question2",
            "label": "Describe your experience",
            "type": "long text"
        },
        {
            "name": "question3",
            "label": "Choose your favorite color",
            "type": "Drop Down"
        }
    ]
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())