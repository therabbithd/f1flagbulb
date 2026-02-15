"""
Test script for NASCAR monitor.
This demonstrates how to extract and display the flag from the NASCAR endpoint.
"""
import asyncio
from nascar_monitor import NascarMonitor, get_flag_name
from config import NASCAR_COLORS

def log_message(msg):
    """Simple logger function."""
    print(msg)

async def on_nascar_update(update):
    """Callback function that processes NASCAR flag updates."""
    if 'NascarFlag' in update:
        flag_data = update['NascarFlag']
        flag_state = flag_data['flag_state']
        flag_name = flag_data['flag_name']
        
        # Get color info if available
        color_info = NASCAR_COLORS.get(flag_state)
        if color_info:
            hue, sat, bright, label, color_hex = color_info
            print(f"\n{'='*50}")
            print(f"Bandera NASCAR: {flag_name}")
            print(f"Código: {flag_state}")
            print(f"Color: {color_hex} ({label})")
            print(f"Vuelta: {flag_data.get('lap_number', 'N/A')}")
            print(f"Tiempo transcurrido: {flag_data.get('elapsed_time', 'N/A')}s")
            print(f"Race ID: {flag_data.get('race_id', 'N/A')}")
            print(f"{'='*50}\n")
        else:
            print(f"Bandera: {flag_name} (código: {flag_state})")

async def main():
    """Main function to run the NASCAR monitor."""
    print("Iniciando monitor de NASCAR...")
    print("Presiona Ctrl+C para detener\n")
    
    monitor = NascarMonitor(on_nascar_update, log_message, poll_interval=5)
    
    try:
        await monitor.run()
    except KeyboardInterrupt:
        print("\n\nMonitor detenido por el usuario.")

if __name__ == "__main__":
    asyncio.run(main())

