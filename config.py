import os
import json

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception:
        pass

settings = load_settings()

# --- CONFIGURATION FROM SETTINGS ---
KASA_USERNAME = settings.get("KASA_USERNAME", "")
KASA_PASSWORD = settings.get("KASA_PASSWORD", "")
KASA_IP = settings.get("KASA_IP", "")
DELAY = settings.get("DELAY", 0)

# --- SIGNALR CONSTANTS ---
SIGNALR_HUB = "Streaming"
F1_UA = "BestHTTP"

# --- COLOR MAPPING ---
# Format: (Hue, Saturation, Brightness, Label, ColorHex)
COLORS = {
    "1": (120, 100, 50, "Pista Libre", "#00FF00"),   # Green
    "2": (60, 100, 50, "Bandera Amarilla", "#FFFF00"), # Yellow
    "3": (60, 100, 50, "Bandera Amarilla", "#FFFF00"), # Yellow
    "4": (30, 100, 70, "Safety Car", "#FFA500"),      # Orange
    "5": (0, 100, 50, "Bandera Roja", "#FF0000"),      # Red
    "6": (300, 100, 50, "VSC", "#FF00FF"),             # Magenta
    "7": (300, 100, 30, "VSC Terminando", "#800080"),  # Dim Magenta
}

# --- NASCAR FLAG MAPPING ---
# Maps NASCAR flag_state codes to colors (same format as COLORS)
# Format: (Hue, Saturation, Brightness, Label, ColorHex)
# Using strings as keys for compatibility with the color system
NASCAR_COLORS = {
    "0": (0, 0, 0, "None", "#000000"),                    # None - Black
    "1": (120, 100, 50, "Green", "#00FF00"),              # Green
    "2": (60, 100, 50, "Yellow", "#FFFF00"),               # Yellow
    "3": (0, 100, 50, "Red", "#FF0000"),                  # Red
    "4": (0, 0, 100, "White", "#FFFFFF"),                 # White
    "5": (0, 0, 50, "Checkered", "#808080"),              # Checkered - Gray
    "6": (180, 100, 50, "Who Knows 1", "#00FFFF"),        # Who Knows 1 - Cyan
    "7": (240, 100, 50, "Who Knows 2", "#0000FF"),        # Who Knows 2 - Blue
    "8": (0, 100, 70, "Hot Track", "#FF3300"),            # Hot Track - Orange-Red
    "9": (200, 100, 50, "Cold Track", "#0066FF"),        # Cold Track - Blue
}

# --- MOTOGP FLAG MAPPING ---
MOTOGP_COLORS = {
    "G": (120, 100, 50, "Pista Libre", "#00FF00"),        # Green
    "Y": (60, 100, 50, "Bandera Amarilla", "#FFFF00"),     # Yellow
    "R": (0, 100, 50, "Bandera Roja", "#FF0000"),          # Red
    "F": (0, 0, 50, "Bandera a Cuadros", "#808080"),       # Chequered / Finished
    "C": (0, 100, 50, "Bandera Roja", "#FF0000"),          # Cancelled? treating as red
}
