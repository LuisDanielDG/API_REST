import requests
import web

urls = (
    '/', 'index',
    '/champion', 'champion',
)

app = web.application(urls, globals())
render = web.template.render('templates')

class index:
    def GET(self):
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions = requests.get(versions_url).json()
        latest_version = versions[0]
        
        url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
        response = requests.get(url)
        data = response.json()
        champions = data["data"]
        
        champion_list = sorted([champ_name for champ_name in champions.keys()])
        
        return render.index(len(champions), champion_list)

class champion:
    def GET(self):
        i = web.input(name=None)
        search_name = i.name.strip() if i.name else None
        
        if not search_name:
            raise web.seeother('/')
        
        versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions = requests.get(versions_url).json()
        latest_version = versions[0]
        
        url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
        response = requests.get(url)
        data = response.json()
        champions_data = data["data"]
        
        search_normalized = search_name.lower().replace(" ", "")
        
        champion_name = None
        for champ_key in champions_data.keys():
            if champ_key.lower() == search_normalized or champ_key.lower().replace(" ", "") == search_normalized:
                champion_name = champ_key
                break
        
        if not champion_name:
            for champ_key in champions_data.keys():
                if search_normalized in champ_key.lower():
                    champion_name = champ_key
                    break
        
        if not champion_name:
            similar = [champ for champ in champions_data.keys() if search_normalized[:3] in champ.lower()]
            error_msg = f"Campeon no encontrado: {search_name}"
            if similar:
                error_msg += f". Quisiste decir: {', '.join(similar[:5])}?"
            return render.error(error_msg)
        
        url_particular = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion/{champion_name}.json"
        
        try:
            champion_data = requests.get(url_particular).json()
            champ = champion_data["data"][champion_name]
            
            splash_url = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion_name}_0.jpg"
            
            skins = []
            if "skins" in champ:
                for skin in champ["skins"]:
                    skin_num = skin["num"]
                    if skin_num == 0:
                        continue
                    skin_name = skin["name"]
                    skin_splash = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion_name}_{skin_num}.jpg"
                    skins.append({
                        "name": skin_name,
                        "splash": skin_splash,
                        "num": skin_num
                    })
            
            return render.champion(champ["name"], champ["title"], champ["blurb"], latest_version, splash_url, skins)
        except Exception as e:
            return render.error(f"Error al cargar el campeon: {str(e)}")

if __name__ == "__main__":
    app.run()
