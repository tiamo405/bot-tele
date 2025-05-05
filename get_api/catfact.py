import requests

def get_cat_fact():
    url = "https://catfact.ninja/fact"
    response = requests.get(url)
    data = response.json()
    return data["fact"]
if __name__ == "__main__":
    print(get_cat_fact())
