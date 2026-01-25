from kasa import Discover
from config import COLORS

class KasaManager:
    """Manages the connection and control of the Kasa smart bulb."""
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.device = None
        self.connected = False

    async def connect(self):
        try:
            self.device = await Discover.discover_single(
                self.ip, username=self.username, password=self.password
            )
            await self.device.update()
            if not self.device.is_on:
                await self.device.turn_on()
            self.connected = True
            return f"Bombilla conectada: {self.device.alias}"
        except Exception as e:
            self.connected = False
            raise Exception(f"No se pudo conectar a la bombilla: {e}")

    async def set_color(self, status_code, logger=None):
        if not self.device: return
        color_info = COLORS.get(status_code)
        if color_info:
            h, s, v, label, _ = color_info
            try:
                if hasattr(self.device, "modules") and "light" in self.device.modules:
                    await self.device.modules["light"].set_hsv(h, s, v)
                else:
                    await self.device.set_hsv(h, s, v)
                await self.device.update()
                if logger: logger(f"[Kasa] Color cambiado a {label}")
            except Exception as e:
                if logger: logger(f"[Kasa Error] Error al cambiar color: {e}")
