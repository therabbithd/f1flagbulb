import tkinter as tk
import customtkinter as ctk
import asyncio
import time
from config import COLORS

class F1FlagApp(ctk.CTk):
    def __init__(self, kasa_mgr, monitor_thread_loop):
        super().__init__()
        self.kasa_mgr = kasa_mgr
        self.monitor_thread_loop = monitor_thread_loop
        self.current_status_code = "1"
        self.terminal_logs = []
        
        self.title("F1 Flag Monitor")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        self._setup_ui()
        self.update_status_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header = ctk.CTkLabel(self, text="F1 FLAG MONITOR", font=("Impact", 40))
        self.header.grid(row=0, column=0, pady=20)

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
        
        self.f1_status_led = ctk.CTkLabel(self.conn_info, text="● F1 Live Timing", text_color="red")
        self.f1_status_led.pack(anchor="w", padx=10, pady=5)
        
        self.bulb_status_led = ctk.CTkLabel(self.conn_info, text="● Kasa Smart Bulb", text_color="red")
        self.bulb_status_led.pack(anchor="w", padx=10, pady=5)

        self.log_textbox = ctk.CTkTextbox(self, height=200)
        self.log_textbox.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_textbox.configure(state="disabled")

        self.controls = ctk.CTkFrame(self)
        self.controls.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(self.controls, text="Probar Color:").pack(side="left", padx=10)
        for code in ["1", "2", "5", "6"]:
            btn = ctk.CTkButton(self.controls, text=COLORS[code][3], width=100, 
                               fg_color=COLORS[code][4], text_color="black" if code in ["1","2"] else "white",
                               command=lambda c=code: self.manual_test(c))
            btn.pack(side="left", padx=5)

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

    def update_status_ui(self, f1_connected=False):
        color_info = COLORS.get(self.current_status_code, (0, 0, 0, "Desconocido", "#333333"))
        h, s, v, label, color_hex = color_info
        self.track_status_text.configure(text=label, text_color=color_hex, font=("Inter", 24, "bold"))
        self.track_status_box.configure(border_width=2, border_color=color_hex)
        self.f1_status_led.configure(text_color="green" if f1_connected else "red")
        self.bulb_status_led.configure(text_color="green" if self.kasa_mgr.connected else "red")
