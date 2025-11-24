import requests
import time
import os

# Reemplaza con tu API key
API_KEY = os.getenv("RIOT_API_KEY")
REGION = "euw1"  # Europa West

headers = {"X-Riot-Token": API_KEY}

# Opción 1: Si conoces el PUUID directamente
def test_by_puuid(puuid):
    url = f"https://{REGION}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}"
    
    print(f"Testing API with PUUID: {puuid[:20]}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API KEY FUNCIONA!")
        print(f"Name: {data.get('name', 'N/A')}")
        print(f"Level: {data['summonerLevel']}")
        return data
    else:
        print(f"❌ Error {response.status_code}: {response.text[:200]}")
        return None

# Opción 2: Obtener PUUID desde ACCOUNT API (más reciente)
def get_puuid_from_name(game_name, tag_line):
    """
    Riot ID format: GameName#TagLine
    Ejemplo: "LUA Iyuster#EUW"
    """
    # IMPORTANTE: Usa ACCOUNT-V1 API, no TFT API
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    
    print(f"Buscando Riot ID: {game_name}#{tag_line}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ PUUID encontrado: {data['puuid'][:20]}...")
        return data['puuid']
    else:
        print(f"❌ Error {response.status_code}: {response.text[:200]}")
        return None

# Test completo
def test_full_workflow():
    # Paso 1: Obtener PUUID desde Riot ID
    # IMPORTANTE: Riot IDs tienen formato "Name#TAG"
    game_name = "LUA Iyuster"
    tag_line = "TETON"  # O el tag que uses (mira en tu cliente)
    
    puuid = get_puuid_from_name(game_name, tag_line)
    
    if not puuid:
        print("\n⚠️  No se pudo obtener PUUID. Verifica tu Riot ID (Name#TAG)")
        return
    
    time.sleep(1)
    
    # Paso 2: Obtener datos de summoner con PUUID
    summoner_data = test_by_puuid(puuid)
    
    if not summoner_data:
        return
    
    time.sleep(1)
    
    # Paso 3: Obtener historial de matches
    url = f"https://{ROUTING}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=5"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        matches = response.json()
        print(f"\n✅ Encontradas {len(matches)} partidas")
        print(f"Primera partida: {matches[0]}")
    else:
        print(f"\n❌ Error obteniendo matches: {response.status_code}")

if __name__ == "__main__":
    print("="*60)
    print("TEST DE API DE RIOT (ENDPOINTS CORRECTOS)")
    print("="*60 + "\n")
    
    test_full_workflow()
    
    print("\n" + "="*60)
    print("Tests completados")
    print("="*60)