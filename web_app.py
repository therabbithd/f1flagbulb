import asyncio
import threading
import time
from flask import Flask, render_template, jsonify, request
from config import KASA_IP, KASA_USERNAME, KASA_PASSWORD, COLORS
from kasa_manager import KasaManager
from f1_monitor import F1Monitor

app = Flask(__name__)

# Global instances
kasa_mgr = KasaManager(KASA_IP, KASA_USERNAME, KASA_PASSWORD)
monitor = None
current_status = {"code": "1", "label": "Pista Libre", "color": "#00FF00"}
f1_connected = False
last_log = ""

def add_log(msg):
    global last_log
    timestamp = time.strftime("%H:%M:%S")
    last_log = f"[{timestamp}] {msg}"
    print(last_log)

async def on_f1_update(update):
    global current_status, f1_connected
    if 'TrackStatus' in update:
        status_code = update['TrackStatus'].get('Status')
        if status_code:
            color_info = COLORS.get(status_code)
            if color_info:
                current_status = {
                    "code": status_code,
                    "label": color_info[3],
                    "color": color_info[4]
                }
            await kasa_mgr.set_color(status_code, add_log)

def start_monitor_loop():
    global monitor
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    monitor = F1Monitor(on_f1_update, add_log)
    
    # Kasa connection
    try:
        loop.run_until_complete(kasa_mgr.connect())
    except Exception as e:
        print(f"Kasa connection failed: {e}")
    
    # Monitor run
    loop.run_until_complete(monitor.run())

@app.route('/')
def index():
    return render_template('index.html', kasa_ip=kasa_mgr.ip)

@app.route('/api/status')
def get_status():
    global f1_connected
    # Check if monitor is connected (monitor.connected is available in F1Monitor)
    is_f1_conn = monitor.connected if monitor else False
    
    return jsonify({
        "status": current_status,
        "f1_connected": is_f1_conn,
        "bulb_connected": kasa_mgr.connected,
        "log": last_log,
        "kasa_ip": kasa_mgr.ip
    })

@app.route('/api/config/ip', methods=['POST'])
def update_ip():
    data = request.json
    new_ip = data.get('ip')
    if new_ip:
        kasa_mgr.update_ip(new_ip)
        # Trigger reconnection in background loop? 
        # Since KasaManager.connect is async, we need to schedule it in the loop
        if monitor and monitor.ws: # Use monitor's loop if running, or just run in new temp loop if not ideal.
             # Actually, simpler is to just call connect() next time we try to set color?
             # But we want immediate feedback.
             # Let's try to schedule it.
             # We rely on the background thread loop.
             # Ideally we should have a way to access that loop.
             pass
        
        # For now, let's just attempt a quick connect if possible or handle it gracefully.
        # Since we are in Flask thread, we can't await easily.
        # We'll just update the IP and let the next attempt (or a separate thread) handle it.
        # But to be robust, let's spawn a thread or task.
        
        threading.Thread(target=lambda: asyncio.run(kasa_mgr.connect()), daemon=True).start()
        
        return jsonify({"success": True, "message": f"IP actualizada a {new_ip}"})
    return jsonify({"success": False, "message": "IP invalida"}), 400

@app.route('/api/test_color', methods=['POST'])
def test_color():
    data = request.json
    code = data.get('code')
    if code:
        # Update UI state immediately
        color_info = COLORS.get(code)
        if color_info:
            global current_status
            current_status = {
                "code": code,
                "label": color_info[3],
                "color": color_info[4]
            }
        
        # Trigger bulb change
        threading.Thread(target=lambda: asyncio.run(kasa_mgr.set_color(code, add_log)), daemon=True).start()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

if __name__ == "__main__":
    # Start Monitor in background
    t = threading.Thread(target=start_monitor_loop, daemon=True)
    t.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
