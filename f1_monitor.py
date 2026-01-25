import json
import base64
import zlib
import requests
import asyncio
import websockets
from urllib.parse import quote
from config import SIGNALR_HUB, F1_UA

class F1Monitor:
    """Handles the connection to F1 Live Timing and data processing."""
    def __init__(self, on_update_callback, logger):
        self.on_update = on_update_callback
        self.log = logger
        self.connected = False
        self.loop = None

    def decompress(self, data):
        try:
            decoded = base64.b64decode(data)
            inflated = zlib.decompress(decoded, -zlib.MAX_WBITS).decode('utf-8')
            return json.loads(inflated)
        except Exception:
            return {}

    async def process_message(self, raw_data):
        try:
            parsed = json.loads(raw_data)
            if 'M' in parsed and isinstance(parsed['M'], list):
                for message in parsed['M']:
                    if message.get('M') == 'feed':
                        field, value = message['A']
                        if field.endswith('.z'):
                            value = self.decompress(value)
                            field = field.split('.')[0]
                        await self.on_update({field: value})
            elif 'R' in parsed and (parsed.get('I') == '1' or parsed.get('I') == 1):
                bulk = {}
                for f, v in parsed['R'].items():
                    if f.endswith('.z'):
                        v = self.decompress(v)
                        f = f.split('.')[0]
                    bulk[f] = v
                await self.on_update(bulk)
        except Exception: pass

    async def run(self):
        self.loop = asyncio.get_running_loop()
        hub_encoded = quote(f'[{{"name":"{SIGNALR_HUB}"}}]', safe='')
        negotiate_url = f"https://livetiming.formula1.com/signalr/negotiate?connectionData={hub_encoded}&clientProtocol=1.5"
        
        while True:
            try:
                self.connected = False
                self.log("[F1] Negociando con el servidor...")
                resp = requests.get(negotiate_url, headers={'User-Agent': F1_UA})
                token = resp.json().get('ConnectionToken')
                if not token:
                    self.log("[F1] No hay sesión activa. Reintentando en 60s...")
                    await asyncio.sleep(60)
                    continue

                ws_url = (f"wss://livetiming.formula1.com/signalr/connect"
                          f"?clientProtocol=1.5&transport=webSockets"
                          f"&connectionToken={quote(token, safe='')}&connectionData={hub_encoded}")
                
                self.log("[F1] Conectando al WebSocket...")
                async with websockets.connect(ws_url, extra_headers={"User-Agent": F1_UA}, ping_interval=None) as ws:
                    self.connected = True
                    self.log("[F1] Conexión establecida")
                    
                    await ws.send(json.dumps({
                        "H": SIGNALR_HUB, "M": "Subscribe",
                        "A": [['TrackStatus', 'RaceControlMessages', 'SessionInfo']], "I": "1"
                    }))

                    async for msg in ws:
                        await self.process_message(msg)
            except Exception as e:
                self.connected = False
                self.log(f"[F1 Error] {e}. Reconectando en 10s...")
                await asyncio.sleep(10)
