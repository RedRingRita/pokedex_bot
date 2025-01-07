import random, os, requests

from dotenv import load_dotenv
from atproto import Client, client_utils
from atproto_client.models.app.bsky.embed.defs import AspectRatio

load_dotenv() # Sert à loader le .env

# clientBluesky = Client()
# clientBluesky.login(os.getenv("bluesky_login_pokedex"), os.getenv("bluesky_password_pokedex"))



response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025&offset=0")
list_pkmn = response.json()
random_pkmn = random.choice(list_pkmn["results"])["name"]

french_random_pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{random_pkmn}").json()["names"][4]["name"]

print(french_random_pkmn)


response = requests.get("https://pokeapi.co/api/v2/pokemon-species/pikachu")
pikachu = response.json()
pokedex_entry = pikachu["flavor_text_entries"][32]["flavor_text"]
