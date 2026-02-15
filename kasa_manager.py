from kasa import Discover
from config import COLORS, NASCAR_COLORS

class KasaManager:
    """Manages the connection and control of the Kasa smart bulb."""
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.device = None
        self.connected = False
        self.current_series = "f1"  # "f1" or "nascar"

    def update_ip(self, new_ip):
        self.ip = new_ip
        self.connected = False
        self.device = None

    def set_series(self, series):
        """Set the current racing series: 'f1' or 'nascar'"""
        self.current_series = series.lower()

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
        # Try to connect if not connected
        if not self.connected or not self.device:
            try:
                await self.connect()
                if logger: logger("[Kasa] Reconectando...")
            except Exception as e:
                if logger: logger(f"[Kasa] No se pudo conectar: {e}")
                return
        
        if not self.device:
            if logger: logger("[Kasa] Dispositivo no disponible")
            return
        
        # Convert to string if needed
        code_str = str(status_code) if status_code is not None else None
        
        # Get color info based on current series
        if self.current_series == "nascar":
            color_info = NASCAR_COLORS.get(code_str)
        else:
            color_info = COLORS.get(code_str)
        
        if color_info:
            h, s, v, label, _ = color_info
            try:
                # Ensure device is on
                if not self.device.is_on:
                    await self.device.turn_on()
                    await self.device.update()
                
                # Set color using HSV
                if hasattr(self.device, "modules") and "light" in self.device.modules:
                    await self.device.modules["light"].set_hsv(h, s, v)
                else:
                    await self.device.set_hsv(h, s, v)
                await self.device.update()
                if logger: logger(f"[Kasa] Color cambiado a {label} (HSV: {h}, {s}, {v})")
            except Exception as e:
                if logger: logger(f"[Kasa Error] Error al cambiar color: {e}")
                self.connected = False
        else:
            if logger: logger(f"[Kasa] Código de bandera no reconocido: {code_str} (serie: {self.current_series})")
