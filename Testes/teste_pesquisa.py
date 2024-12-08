from serpapi import GoogleSearch

params = {
    "q": "coffee",
    "engine": "google",
    "api_key": "d6ccb17175bc57498fba26947fa270348792aca335e7d2eb8c651482f18b3952"  # Replace with your actual API key
}

search = GoogleSearch(params)
results = search.get_dict()

#print(results)