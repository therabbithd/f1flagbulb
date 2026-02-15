import asyncio
import threading
from config import KASA_IP, KASA_USERNAME, KASA_PASSWORD
from kasa_manager import KasaManager
from f1_monitor import F1Monitor
from nascar_monitor import NascarMonitor
from gui import F1FlagApp

async def main_logic(app):
    monitor_thread_loop = asyncio.get_running_loop()
    app.monitor_thread_loop = monitor_thread_loop
    app.series_change_event = asyncio.Event()
    
    kasa_mgr = app.kasa_mgr
    try:
        msg = await kasa_mgr.connect()
        app.add_log(msg)
    except Exception as e:
        app.add_log(str(e))

    current_monitor = None
    monitor_task = None
    stop_monitor = asyncio.Event()
    last_series = app.selected_series
    
    # State tracking for flags
    last_f1_status = None
    last_nascar_status = None

    async def on_f1_update(update):
        nonlocal last_f1_status
        if 'TrackStatus' in update:
            status = update['TrackStatus'].get('Status')
            if status:
                status_str = str(status)
                # Only update if status has changed
                if status_str != last_f1_status:
                    last_f1_status = status_str
                    app.current_status_code = status_str
                    app.after(0, lambda: app.update_status_ui(current_monitor.connected if current_monitor else False))
                    # Change bulb color immediately
                    await kasa_mgr.set_color(status_str, app.add_log)

    async def on_nascar_update(update):
        nonlocal last_nascar_status
        if 'NascarFlag' in update:
            flag_data = update['NascarFlag']
            flag_state = flag_data.get('flag_state')
            if flag_state is not None:
                flag_state_str = str(flag_state)
                # Only update if status has changed
                if flag_state_str != last_nascar_status:
                    last_nascar_status = flag_state_str
                    app.current_status_code = flag_state_str
                    app.after(0, lambda: app.update_status_ui(current_monitor.connected if current_monitor else False))
                    # Change bulb color immediately
                    await kasa_mgr.set_color(flag_state_str, app.add_log)

    async def run_monitor():
        nonlocal current_monitor, monitor_task, last_series
        while not stop_monitor.is_set():
            # Get current series from app
            series = app.selected_series
            
            # If series changed, stop current monitor
            if series != last_series:
                if monitor_task and not monitor_task.done():
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except (asyncio.CancelledError, Exception):
                        pass
                monitor_task = None
                current_monitor = None
                last_series = series
            
            # Create and start appropriate monitor if not running
            if not monitor_task or monitor_task.done():
                # Update KasaManager series before starting monitor
                kasa_mgr.set_series(series)
                
                if series == "f1":
                    current_monitor = F1Monitor(on_f1_update, app.add_log)
                    app.add_log("[Sistema] Iniciando monitor F1...")
                    # Update bulb immediately to last known F1 status if available
                    if last_f1_status:
                        await kasa_mgr.set_color(last_f1_status, app.add_log)
                else:
                    current_monitor = NascarMonitor(on_nascar_update, app.add_log, poll_interval=5)
                    app.add_log("[Sistema] Iniciando monitor NASCAR...")
                    # Update bulb immediately to last known NASCAR status if available
                    if last_nascar_status:
                        await kasa_mgr.set_color(last_nascar_status, app.add_log)
                
                monitor_task = asyncio.create_task(current_monitor.run())
            
            # Wait for series change or monitor completion
            try:
                # Check for series change periodically
                while not stop_monitor.is_set():
                    try:
                        await asyncio.wait_for(app.series_change_event.wait(), timeout=0.5)
                        if app.selected_series != series:
                            app.series_change_event.clear()
                            break
                    except asyncio.TimeoutError:
                        # Check if monitor task is still running
                        if monitor_task and monitor_task.done():
                            # Monitor stopped, restart it
                            break
                        # Continue waiting
                        continue
            except Exception as e:
                app.add_log(f"[Sistema Error] {e}")
                await asyncio.sleep(1)

    # Update UI periodically for connection status
    def update_conn_ui():
        if current_monitor:
            app.after(0, lambda: app.update_status_ui(current_monitor.connected))
        timer = threading.Timer(5, update_conn_ui)
        timer.daemon = True
        timer.start()
    
    update_conn_ui()
    
    try:
        await run_monitor()
    except asyncio.CancelledError:
        pass
    finally:
        stop_monitor.set()
        if monitor_task:
            monitor_task.cancel()

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
