import requests

def get_cat_fact():
    url = "https://catfact.ninja/fact"
    response = requests.get(url)
    data = response.json()
    return data["fact"]

print(get_cat_fact())
