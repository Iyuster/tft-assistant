"""
Módulo para obtener información de partida activa/en vivo
"""
import requests


def fetch_active_game(api_key, region, puuid):
    """
    Obtiene información de la partida activa si el summoner está jugando
    
    Args:
        api_key: Riot API key
        region: Región (euw1, na1, etc.)
        puuid: PUUID del summoner
    
    Returns:
        dict con información de la partida activa, o None si no está en partida
    """
    url = f"https://{region}.api.riotgames.com/tft/spectator/v5/active-games/by-puuid/{puuid}"
    headers = {"X-Riot-Token": api_key}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # El jugador está en partida
            return response.json()
        elif response.status_code == 404:
            # El jugador no está en partida (esto es normal)
            return None
        else:
            # Otro error (rate limit, api key inválido, etc.)
            print(f"Error checking active game: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking active game: {e}")
        return None


def parse_active_game_info(game_data):
    """
    Parsea la información de la partida activa para mostrar en UI
    
    Args:
        game_data: Datos de la partida activa desde la API
    
    Returns:
        dict con información parseada
    """
    if not game_data:
        return None
    
    return {
        'game_id': game_data.get('gameId'),
        'game_length': game_data.get('gameLength', 0),  # Segundos desde el inicio
        'game_mode': game_data.get('gameMode', 'TFT'),
        'participants_count': len(game_data.get('participants', [])),
        'queue_id': game_data.get('gameQueueConfigId'),
    }
