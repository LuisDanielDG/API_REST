import requests

versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
versions = requests.get(versions_url).json()

latest_version = versions[0]
print("Latest version:", latest_version)

version = latest_version

url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"

champion_name = input("Ingresa el campeón a investigar: ").strip().replace(" ", "").replace("'", "").title()

url_particular = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion/{champion_name}.json"
champion_data = requests.get(url_particular).json()

response = requests.get(url)
data = response.json()

champions = data["data"]
champion = champion_data["data"][f"{champion_name}"]

print("Total champions:", len(champions))
print(champion["name"])
print(champion["title"])
print(champions[f"{champion_name}"])
