import tkinter as tk
import customtkinter as ctk
import asyncio
import time
import ctypes
import os
import sys
from config import COLORS, NASCAR_COLORS, MOTOGP_COLORS

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class F1FlagApp(ctk.CTk):
    def __init__(self, kasa_mgr, monitor_thread_loop):
        super().__init__()
        self.kasa_mgr = kasa_mgr
        self.monitor_thread_loop = monitor_thread_loop
        self.current_status_code = "1"
        self.terminal_logs = []
        self.selected_series = "f1"  # "f1" or "nascar"
        self.monitor_connected = False
        
        # This tells Windows to use the app's icon instead of Python's default icon
        try:
            myappid = u'f1flag.monitor.app.1' 
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
            
        self.title("Racing Flag Monitor")
        icon_file = resource_path("icon.ico")
        try:
            from PIL import Image, ImageTk
            import math
            img = Image.open(icon_file)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Windows automatically stretches rectangular icons to a square, 
            # so we pad it with transparent pixels to be a perfect square.
            max_dim = max(img.size)
            square_img = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 0))
            offset = ((max_dim - img.size[0]) // 2, (max_dim - img.size[1]) // 2)
            square_img.paste(img, offset)
            
            icon_img = ImageTk.PhotoImage(square_img)
            self.wm_iconphoto(True, icon_img)
            self.iconbitmap(icon_file)
        except Exception as e:
            print("Error parsing icon:", e)
            self.iconbitmap(icon_file)
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        self._setup_ui()
        self.update_status_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header with series selector
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, pady=20, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.header = ctk.CTkLabel(header_frame, text="RACING FLAG MONITOR", font=("Impact", 40))
        self.header.grid(row=0, column=1, padx=20)
        
        # Series selector
        selector_frame = ctk.CTkFrame(header_frame)
        selector_frame.grid(row=0, column=0, padx=20)
        ctk.CTkLabel(selector_frame, text="Serie:", font=("Inter", 12)).pack(side="left", padx=5)
        self.series_selector = ctk.CTkSegmentedButton(
            selector_frame, 
            values=["F1", "NASCAR", "MotoGP"],
            command=self.on_series_change
        )
        self.series_selector.pack(side="left", padx=5)
        self.series_selector.set("F1")

        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.track_status_box = ctk.CTkFrame(self.status_frame, width=300, height=150)
        self.track_status_box.pack(side="left", padx=20, pady=20)
        self.track_status_box.pack_propagate(False)
        
        ctk.CTkLabel(self.track_status_box, text="ESTADO DE PISTA", font=("Inter", 12)).pack(pady=(15,0))
        self.track_status_text = ctk.CTkLabel(self.track_status_box, text="Cargando...", font=("Inter", 12, "bold"))
        self.track_status_text.pack(expand=True)

        self.conn_info = ctk.CTkFrame(self.status_frame)
        self.conn_info.pack(side="right", padx=20, pady=20, fill="both", expand=True)
        
        self.monitor_status_led = ctk.CTkLabel(self.conn_info, text="● F1 Live Timing", text_color="red")
        self.monitor_status_led.pack(anchor="w", padx=10, pady=5)
        
        self.bulb_status_led = ctk.CTkLabel(self.conn_info, text="● Kasa Smart Bulb", text_color="red")
        self.bulb_status_led.pack(anchor="w", padx=10, pady=5)

        # Configuration Frame
        self.config_frame = ctk.CTkFrame(self.conn_info, fg_color="transparent")
        self.config_frame.pack(anchor="w", padx=10, pady=(10, 0), fill="x")
        
        self.settings_btn = ctk.CTkButton(self.config_frame, text="⚙️ Configuración", width=120, command=self.open_settings_window)
        self.settings_btn.pack(side="left")

        self.log_textbox = ctk.CTkTextbox(self, height=200)
        self.log_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_textbox.configure(state="disabled")

        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        self.test_label = ctk.CTkLabel(self.controls, text="Probar Color:")
        self.test_label.pack(side="left", padx=10)
        
        self.test_buttons_frame = ctk.CTkFrame(self.controls)
        self.test_buttons_frame.pack(side="left", padx=5)
        
        self._update_test_buttons()

    def open_settings_window(self):
        if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return
            
        import config
        self.settings_window = ctk.CTkToplevel(self)
        self.settings_window.title("Configuración")
        self.settings_window.geometry("300x380")
        self.settings_window.attributes("-topmost", True)
        
        ctk.CTkLabel(self.settings_window, text="KASA IP:").pack(pady=(10, 0))
        ip_entry = ctk.CTkEntry(self.settings_window)
        ip_entry.pack(pady=5)
        ip_entry.insert(0, config.settings.get("KASA_IP", ""))
        
        ctk.CTkLabel(self.settings_window, text="KASA Username:").pack()
        user_entry = ctk.CTkEntry(self.settings_window)
        user_entry.pack(pady=5)
        user_entry.insert(0, config.settings.get("KASA_USERNAME", ""))
        
        ctk.CTkLabel(self.settings_window, text="KASA Password:").pack()
        
        pass_frame = ctk.CTkFrame(self.settings_window, fg_color="transparent")
        pass_frame.pack(pady=5)
        
        pass_entry = ctk.CTkEntry(pass_frame, show="*", width=160)
        pass_entry.pack(side="left")
        pass_entry.insert(0, config.settings.get("KASA_PASSWORD", ""))
        
        def toggle_password():
            if pass_entry.cget("show") == "*":
                pass_entry.configure(show="")
                show_btn.configure(text="Ocultar")
            else:
                pass_entry.configure(show="*")
                show_btn.configure(text="Mostrar")
                
        show_btn = ctk.CTkButton(pass_frame, text="Mostrar", width=60, command=toggle_password)
        show_btn.pack(side="left", padx=(5, 0))
        
        ctk.CTkLabel(self.settings_window, text="Delay (segundos):").pack()
        delay_entry = ctk.CTkEntry(self.settings_window)
        delay_entry.pack(pady=5)
        delay_entry.insert(0, str(config.settings.get("DELAY", 0)))
        
        def save():
            new_ip = ip_entry.get()
            new_user = user_entry.get()
            new_pass = pass_entry.get()
            try:
                new_delay = int(delay_entry.get())
            except ValueError:
                new_delay = 0

            config.settings["KASA_IP"] = new_ip
            config.settings["KASA_USERNAME"] = new_user
            config.settings["KASA_PASSWORD"] = new_pass
            config.settings["DELAY"] = new_delay
            config.save_settings(config.settings)
            
            # Update running manager
            self.kasa_mgr.update_config(new_ip, new_user, new_pass)
            self.add_log(f"Configuración guardada (IP: {new_ip})")
            self.settings_window.destroy()
            asyncio.run_coroutine_threadsafe(self._reconnect_kasa(), self.monitor_thread_loop)
            
        ctk.CTkButton(self.settings_window, text="Guardar", command=save).pack(pady=15)

    async def _reconnect_kasa(self):
        try:
            msg = await self.kasa_mgr.connect()
            self.add_log(msg)
            self.update_status_ui()
        except Exception as e:
            self.add_log(str(e))
            self.update_status_ui()

    def manual_test(self, code):
        self.current_status_code = code
        self.update_status_ui()
        asyncio.run_coroutine_threadsafe(self.kasa_mgr.set_color(code, self.add_log), self.monitor_thread_loop)

    def add_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        self.terminal_logs.append(full_msg)
        if len(self.terminal_logs) > 50: self.terminal_logs.pop(0)
        self.after(0, self._refresh_logs)

    def _refresh_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", "\n".join(self.terminal_logs))
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def on_series_change(self, value):
        """Called when the series selector changes."""
        self.selected_series = value.lower()
        self.kasa_mgr.set_series(self.selected_series)
        
        # Update header
        if value == "F1":
            self.header.configure(text="F1 FLAG MONITOR")
            self.monitor_status_led.configure(text="● F1 Live Timing")
        elif value == "NASCAR":
            self.header.configure(text="NASCAR FLAG MONITOR")
            self.monitor_status_led.configure(text="● NASCAR Live Feed")
        else:
            self.header.configure(text="MOTOGP FLAG MONITOR")
            self.monitor_status_led.configure(text="● MotoGP Live Timing")
        
        # Reset status code
        self.current_status_code = "1"
        self.update_status_ui()
        self._update_test_buttons()
        
        # Notify main logic to switch monitors
        if hasattr(self, 'series_change_event') and self.series_change_event:
            self.series_change_event.set()
    
    def _update_test_buttons(self):
        """Update test buttons based on selected series."""
        # Clear existing buttons
        for widget in self.test_buttons_frame.winfo_children():
            widget.destroy()
        
        # Get color map based on series
        color_map = COLORS if self.selected_series == "f1" else (NASCAR_COLORS if self.selected_series == "nascar" else MOTOGP_COLORS)
        
        # Select test codes based on series
        if self.selected_series == "f1":
            test_codes = ["1", "2", "5", "6"]
        elif self.selected_series == "motogp":
            test_codes = ["G", "Y", "R", "F"]
        else:
            test_codes = ["1", "2", "3", "5"]  # Green, Yellow, Red, Checkered
        
        for code in test_codes:
            if code in color_map:
                color_info = color_map[code]
                label = color_info[3]
                color_hex = color_info[4]
                text_color = "black" if code in ["1", "2", "4"] else "white"
                
                btn = ctk.CTkButton(
                    self.test_buttons_frame, 
                    text=label, 
                    width=100, 
                    fg_color=color_hex, 
                    text_color=text_color,
                    command=lambda c=code: self.manual_test(c)
                )
                btn.pack(side="left", padx=5)

    def update_status_ui(self, monitor_connected=None):
        """Update the status UI with current flag state."""
        if monitor_connected is not None:
            self.monitor_connected = monitor_connected
        
        # Get color map based on series
        color_map = COLORS if self.selected_series == "f1" else (NASCAR_COLORS if self.selected_series == "nascar" else MOTOGP_COLORS)
        color_info = color_map.get(self.current_status_code, (0, 0, 0, "Desconocido", "#333333"))
        
        h, s, v, label, color_hex = color_info
        self.track_status_text.configure(text=label, text_color=color_hex, font=("Inter", 24, "bold"))
        self.track_status_box.configure(border_width=2, border_color=color_hex)
        self.monitor_status_led.configure(text_color="green" if self.monitor_connected else "red")
        self.bulb_status_led.configure(text_color="green" if self.kasa_mgr.connected else "red")
