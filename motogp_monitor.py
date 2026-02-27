import asyncio
import requests
import json
import time

class MotoGPMonitor:
    """Handles the connection to MotoGP Live Timing and data processing."""
    def __init__(self, on_update_callback, logger):
        self.on_update = on_update_callback
        self.log = logger
        self.connected = False
        self.loop = None
        self.last_status = None

    async def fetch_data(self):
        url = "https://api.motogp.pulselive.com/motogp/v1/timing-gateway/livetiming-lite"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Origin": "https://www.motogp.com",
            "Referer": "https://www.motogp.com/"
        }
        try:
            return await asyncio.to_thread(requests.get, url, headers=headers, timeout=10)
        except Exception as e:
            raise e

    async def run(self):
        self.loop = asyncio.get_running_loop()
        
        while True:
            try:
                self.log("[MotoGP] Consultando API...")
                resp = await self.fetch_data()
                
                if resp.status_code == 200:
                    self.connected = True
                    try:
                        data = resp.json()
                        head = data.get("head", {})
                        status_id = head.get("session_status_id")
                        
                        if status_id and status_id != self.last_status:
                            self.last_status = status_id
                            # Usamos un formato compatible con el callback general
                            await self.on_update({"MotoGPStatus": {"Status": status_id}})
                    except json.JSONDecodeError:
                        self.log("[MotoGP] Respuesta no es JSON válido.")
                elif resp.status_code in [403, 404]:
                    self.connected = False
                    self.log("[MotoGP] No hay sesión activa en este momento.")
                else:
                    self.connected = False
                    self.log(f"[MotoGP] Error HTTP {resp.status_code}")
                
                # MotoGP actualiza seguido durante la carrera. 5-10s
                await asyncio.sleep(10)
                
            except Exception as e:
                self.connected = False
                self.log(f"[MotoGP Error] {e}. Reintentando en 15s...")
                await asyncio.sleep(15)
