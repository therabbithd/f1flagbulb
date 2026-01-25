import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION FROM .ENV ---
KASA_USERNAME = os.getenv("KASA_USERNAME")
KASA_PASSWORD = os.getenv("KASA_PASSWORD")
KASA_IP = os.getenv("KASA_IP")

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
