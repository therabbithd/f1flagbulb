import asyncio
import threading
from config import KASA_IP, KASA_USERNAME, KASA_PASSWORD
from kasa_manager import KasaManager
from f1_monitor import F1Monitor
from gui import F1FlagApp

async def main_logic(app):
    monitor_thread_loop = asyncio.get_running_loop()
    app.monitor_thread_loop = monitor_thread_loop
    
    kasa_mgr = app.kasa_mgr
    try:
        msg = await kasa_mgr.connect()
        app.add_log(msg)
    except Exception as e:
        app.add_log(str(e))

    async def on_f1_update(update):
        if 'TrackStatus' in update:
            status = update['TrackStatus'].get('Status')
            if status:
                app.current_status_code = status
                app.after(0, lambda: app.update_status_ui(monitor.connected))
                await kasa_mgr.set_color(status, app.add_log)

    monitor = F1Monitor(on_f1_update, app.add_log)
    
    # Update UI periodically for connection status
    def update_conn_ui():
        app.after(0, lambda: app.update_status_ui(monitor.connected))
        timer = threading.Timer(5, update_conn_ui)
        timer.daemon = True
        timer.start()
    
    update_conn_ui()
    await monitor.run()

def start_background_loop(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_logic(app))

if __name__ == "__main__":
    kasa_mgr = KasaManager(KASA_IP, KASA_USERNAME, KASA_PASSWORD)
    # The app will be initialized first, then the loop
    app = F1FlagApp(kasa_mgr, None)
    
    # Start F1 Monitor in background
    bg_thread = threading.Thread(target=start_background_loop, args=(app,), daemon=True)
    bg_thread.start()
    
    app.mainloop()
