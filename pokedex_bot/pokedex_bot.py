import random, os, requests

from change_bg_color import change_background
from urllib.parse import quote # Sert à encoder les caractères spéciaux pour l'URL
from dotenv import load_dotenv
from atproto import Client, client_utils
from atproto_client.models.app.bsky.embed.defs import AspectRatio

load_dotenv() # Sert à loader le .env

clientBluesky = Client()
clientBluesky.login(os.getenv("bluesky_login_pokedex"), os.getenv("bluesky_password_pokedex"))

# Choix du pokémon au hasard
def randomizer() :
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025&offset=0")
    list_pkmn = response.json()
    random_pkmn = random.choice(list_pkmn["results"])["name"] # Choix au hasard d'un nom de pokémon dans la liste.
    return random_pkmn

# Récupération des donénes du Pokémon en FRANCAIS.
def get_pkmn_data() :
    # -- -- Récupération du nom en français
    while True :
        random_pkmn = randomizer()

        chosen_pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon/{random_pkmn}").json()
        chosen_pkmn_page2 = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{random_pkmn}").json()

        french_name = next(
            (i["name"] for i in chosen_pkmn_page2.get("names", []) if i["language"]["name"] == "fr"),
            None  # Retourne None si aucun nom en français n'est trouvé
        )
        
        if french_name : # Si on trouve un nom français on sort de la boucle
            break

    # -- -- Récupération de la catégorie
    french_genus = next(
        (i["genus"].replace("Pokémon", "").strip() for i in chosen_pkmn_page2.get("genera", []) if i["language"]["name"] == "fr"),
        None
    )
    
    # -- -- Récupération de l'id, poids et taille
    pkmn_id = chosen_pkmn["id"]
    weight = chosen_pkmn["weight"]
    height = chosen_pkmn["height"]

    # -- Récupération des types
    types_details = []
    types_name = []

    for info in chosen_pkmn["types"] :
        type_url = info["type"]["url"]
        type_data = requests.get(type_url).json()

        # print(types_details)
        type_name = next(
                (j["name"] for j in type_data.get("names", []) if j["language"]["name"] == "fr"),
            None
        )
        types_name.append(type_name)

    # -- -- Récupération du nom de la région d'origine du Pokémon
    origin_region_url = chosen_pkmn_page2["generation"]["url"]
    origin_region = requests.get(origin_region_url).json()
    origin_region_name = origin_region["main_region"]["name"].replace("unova", "unys").capitalize()

    # Création de la liste des entrées française des pokédex (en faisant une compréhension de liste)
    pokedex_entries_fr = [
        entry for entry in chosen_pkmn_page2.get("flavor_text_entries", []) if entry["language"]["name"] == "fr"
    ]

    pokedex_entry_fr = "En attente d'une mise à jour de la base de donnée"
    french_game_version = "française non trouvée"

    if pokedex_entries_fr:  # Vérifie s'il y a des entrées disponibles
        random_pokedex_entry = random.choice(pokedex_entries_fr)
        pokedex_entry_fr = random_pokedex_entry.get("flavor_text", "").replace("\n", " ").strip()

        # -- -- Récupération du nom français de la version du jeu
        game_version_url = random_pokedex_entry.get("version", {}).get("url") #On tente d'obtenir la valeur associée à la clé "version" dans ce dictionnaire. Si cette clé n'existe pas, un dictionnaire vide ({}) est retourné à la place. À partir de la valeur de "version", on tente de récupérer la valeur associée à la clé "url". Si la clé "url" n'existe pas, cela retournera None.
        if game_version_url:
            try:
                games_version = requests.get(game_version_url)
                games_version.raise_for_status() #Cette méthode lève une exception si la requête HTTP retourne une erreur (par exemple, un code 404 ou 500). Si tout va bien, on passe à l'étape suivante.
                games_version = games_version.json()

                french_game_version = next( # On garde la première itération où fr apparait
                    (name["name"] for name in games_version.get("names", []) if name["language"]["name"] == "fr"),
                    "Version française non trouvée"
                )
            except (requests.exceptions.RequestException, KeyError, TypeError):
                french_game_version = "Version française non trouvée"

    # -- -- Récupération de l'artwork
    artwork_response = requests.get(chosen_pkmn["sprites"]["other"]["official-artwork"]["front_default"])
    artwork_data = artwork_response.content # Lire le contenu de l'image en bytes

    changed_bg_artwork = change_background(artwork_data, background_color=(22, 30, 39))

    # Retour sous forme de dictionnaire
    return {
        "name": french_name,
        "genus": french_genus,
        "id": pkmn_id,
        "weight": weight,
        "height": height,
        "types": types_name,
        "pokedex_entry": pokedex_entry_fr,
        "game_version": french_game_version,
        "region": origin_region_name,
        "artwork": changed_bg_artwork
    }

def truncate_to_tweet(pkmn_data, limit=260):
    if len(pkmn_data) <= limit:
        return pkmn_data  # Le texte est déjà dans la limite.
    
    # Limiter au maximum et chercher le dernier espace avant la limite.
    truncated = pkmn_data[:limit] # Coupe le texte pour ne conserver que les 'limit' premiers caractères.
    last_space = truncated.rfind(" ") #  Recherche la position de la dernière occurrence du caractère " " dans le texte tronqué.
    
    if last_space == -1:  # Si aucun espace trouvé dans la limite.
        return truncated.strip() + "…"  # Ajouter une ellipse si aucun point trouvé.
    
    return truncated[:last_space].strip() + "…"  # Ajouter une ellipse après le dernier mot complet.

pokemon_data = get_pkmn_data()

full_pokemon_text = (
    f"{pokemon_data['name']}\n"
    f"N°{pokemon_data['id']}\n"
    f"Région d'origine : {pokemon_data['region']}\n"
    f"Poids : {pokemon_data['weight'] / 10}kg, taille : {pokemon_data['height'] / 10}m\n"
    f"Type : {'- '.join(pokemon_data['types'])}\n"
    f"Pokémon {pokemon_data['genus']}\n"
    f"Version {pokemon_data['game_version']} : {pokemon_data['pokedex_entry']}\n"
    "#Pokémon #Pokédex"
)

tweeted_text = truncate_to_tweet(full_pokemon_text)

formated_name = pokemon_data["name"].replace(" ", "_")
url_safe_name = quote(formated_name) # Encode le nom du pokémon pour l'URL

# text = client_utils.TextBuilder().text(tweeted_text).link('Plus d\'infos', f"https://www.pokepedia.fr/{url_safe_name}").text("\n#Pokémon #Pokédex")
text = client_utils.TextBuilder().text(tweeted_text)
image_data = pokemon_data['artwork']
image_alt = f"Artwork officiel de {pokemon_data['name']}"

publi = clientBluesky.send_image(text, image_data, image_alt)