"""
Ejemplo simple de cómo obtener la bandera de NASCAR.
"""
from nascar_monitor import fetch_nascar_flag, get_flag_name
from config import NASCAR_COLORS

# Método 1: Usar la función simple
print("=== Obteniendo bandera de NASCAR ===")
flag_data = fetch_nascar_flag()

if flag_data:
    flag_state = flag_data['flag_state']
    flag_name = flag_data['flag_name']
    
    print(f"\nBandera: {flag_name}")
    print(f"Código: {flag_state}")
    print(f"Vuelta: {flag_data.get('lap_number', 'N/A')}")
    print(f"Tiempo transcurrido: {flag_data.get('elapsed_time', 'N/A')}s")
    print(f"Race ID: {flag_data.get('race_id', 'N/A')}")
    
    # Obtener información de color si está disponible
    color_info = NASCAR_COLORS.get(flag_state)
    if color_info:
        hue, sat, bright, label, color_hex = color_info
        print(f"Color: {color_hex} ({label})")
else:
    print("No se pudo obtener la bandera")

# Método 2: Usar la función get_flag_name directamente
print("\n=== Mapeo de códigos ===")
for code in range(10):
    flag_name = get_flag_name(code)
    print(f"Código {code}: {flag_name}")

