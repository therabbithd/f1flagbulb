import json
import requests
import asyncio
from config import F1_UA

def get_flag_name(code):
    """Maps NASCAR flag_state code to flag name."""
    switch = {
        0: 'None',
        1: 'Green',
        2: 'Yellow',
        3: 'Red',
        4: 'White',
        5: 'Checkered',
        6: 'Who Knows 1',
        7: 'Who Knows 2',
        8: 'Hot Track',
        9: 'Cold Track'
    }
    return switch.get(code, 'UnAccounted For Flag')

def fetch_nascar_flag():
    """
    Simple function to fetch the current NASCAR flag state.
    Returns a dictionary with flag information or None if error.
    """
    endpoint = "https://cf.nascar.com/live/feeds/live-feed.json"
    try:
        resp = requests.get(endpoint, headers={'User-Agent': F1_UA}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        flag_state = data.get('flag_state')
        
        if flag_state is not None:
            flag_name = get_flag_name(flag_state)
            return {
                'flag_state': flag_state,
                'flag_name': flag_name,
                'lap_number': data.get('lap_number'),
                'elapsed_time': data.get('elapsed_time'),
                'race_id': data.get('race_id'),
                'laps_in_race': data.get('laps_in_race'),
                'laps_to_go': data.get('laps_to_go')
            }
    except Exception as e:
        print(f"Error fetching NASCAR flag: {e}")
    
    return None

class NascarMonitor:
    """Handles the connection to NASCAR Live Feed and data processing."""
    def __init__(self, on_update_callback, logger, poll_interval=5):
        self.on_update = on_update_callback
        self.log = logger
        self.connected = False
        self.poll_interval = poll_interval
        self.endpoint = "https://cf.nascar.com/live/feeds/live-feed.json"

    async def fetch_flag(self):
        """Fetches the current flag state from NASCAR endpoint."""
        try:
            resp = requests.get(self.endpoint, headers={'User-Agent': F1_UA}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            flag_state = data.get('flag_state')
            
            if flag_state is not None:
                flag_name = get_flag_name(flag_state)
                return {
                    'flag_state': flag_state,
                    'flag_name': flag_name,
                    'lap_number': data.get('lap_number'),
                    'elapsed_time': data.get('elapsed_time'),
                    'race_id': data.get('race_id')
                }
        except requests.exceptions.RequestException as e:
            self.log(f"[NASCAR] Error fetching data: {e}")
        except json.JSONDecodeError as e:
            self.log(f"[NASCAR] Error parsing JSON: {e}")
        except Exception as e:
            self.log(f"[NASCAR] Unexpected error: {e}")
        
        return None

    async def run(self):
        """Main monitoring loop that polls the NASCAR endpoint."""
        while True:
            try:
                self.connected = False
                self.log("[NASCAR] Obteniendo estado de bandera...")
                
                flag_data = await self.fetch_flag()
                
                if flag_data:
                    self.connected = True
                    self.log(f"[NASCAR] Bandera: {flag_data['flag_name']} (código: {flag_data['flag_state']})")
                    await self.on_update({'NascarFlag': flag_data})
                else:
                    self.log("[NASCAR] No se pudo obtener el estado de bandera")
                
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                self.connected = False
                self.log(f"[NASCAR Error] {e}. Reintentando en {self.poll_interval}s...")
                await asyncio.sleep(self.poll_interval)

