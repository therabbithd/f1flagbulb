import tkinter as tk
import customtkinter as ctk
import asyncio
import time
from config import COLORS, NASCAR_COLORS

class F1FlagApp(ctk.CTk):
    def __init__(self, kasa_mgr, monitor_thread_loop):
        super().__init__()
        self.kasa_mgr = kasa_mgr
        self.monitor_thread_loop = monitor_thread_loop
        self.current_status_code = "1"
        self.terminal_logs = []
        self.selected_series = "f1"  # "f1" or "nascar"
        self.monitor_connected = False
        
        self.title("Racing Flag Monitor")
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
            values=["F1", "NASCAR"],
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

        # IP Configuration Frame
        self.ip_frame = ctk.CTkFrame(self.conn_info, fg_color="transparent")
        self.ip_frame.pack(anchor="w", padx=10, pady=(10, 0), fill="x")
        
        self.ip_entry = ctk.CTkEntry(self.ip_frame, placeholder_text="IP Bombilla", width=120)
        self.ip_entry.pack(side="left", padx=(0, 5))
        if hasattr(self.kasa_mgr, 'ip') and self.kasa_mgr.ip:
            self.ip_entry.insert(0, self.kasa_mgr.ip)
            
        self.update_ip_btn = ctk.CTkButton(self.ip_frame, text="↻", width=30, command=self.update_kasa_ip)
        self.update_ip_btn.pack(side="left")

    def update_kasa_ip(self):
        new_ip = self.ip_entry.get()
        if new_ip:
            self.add_log(f"Actualizando IP a {new_ip}...")
            self.kasa_mgr.update_ip(new_ip)
            asyncio.run_coroutine_threadsafe(self._reconnect_kasa(), self.monitor_thread_loop)

    async def _reconnect_kasa(self):
        try:
            msg = await self.kasa_mgr.connect()
            self.add_log(msg)
            self.update_status_ui()
        except Exception as e:
            self.add_log(str(e))
            self.update_status_ui()

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
        else:
            self.header.configure(text="NASCAR FLAG MONITOR")
            self.monitor_status_led.configure(text="● NASCAR Live Feed")
        
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
        color_map = COLORS if self.selected_series == "f1" else NASCAR_COLORS
        
        # Select test codes based on series
        if self.selected_series == "f1":
            test_codes = ["1", "2", "5", "6"]
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
        color_map = COLORS if self.selected_series == "f1" else NASCAR_COLORS
        color_info = color_map.get(self.current_status_code, (0, 0, 0, "Desconocido", "#333333"))
        
        h, s, v, label, color_hex = color_info
        self.track_status_text.configure(text=label, text_color=color_hex, font=("Inter", 24, "bold"))
        self.track_status_box.configure(border_width=2, border_color=color_hex)
        self.monitor_status_led.configure(text_color="green" if self.monitor_connected else "red")
        self.bulb_status_led.configure(text_color="green" if self.kasa_mgr.connected else "red")
