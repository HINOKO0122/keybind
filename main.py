import tkinter as tk
from tkinter import ttk
import os
import json
import sys
import winreg
from pynput import keyboard

# --- 定数・パス設定 ---
APP_NAME = "RACEN_KeyCounter"
DATA_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class KeyCounterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KeyCounter")
        
        # データの読み込み
        self.stats = self.load_json(STATS_FILE)
        self.config = self.load_json(CONFIG_FILE, default={"topmost": True, "scale": 1.0, "startup": False})
        
        self.root.attributes("-topmost", self.config["topmost"])
        self.scale = self.config["scale"]
        
        # キー配列定義 [表示名, x, y, 横幅倍率, キーID]
        # RACEN TKL配列を再現 (一部抜粋、後ほど調整可能)
        self.key_map = [
            # Row 1
            ["Esc", 5, 5, 1, "esc"], ["F1", 70, 5, 1, "f1"], ["F2", 110, 5, 1, "f2"], ["F3", 150, 5, 1, "f3"], ["F4", 190, 5, 1, "f4"],
            ["F5", 245, 5, 1, "f5"], ["F6", 285, 5, 1, "f6"], ["F7", 325, 5, 1, "f7"], ["F8", 365, 5, 1, "f8"],
            ["PrtSc", 475, 5, 1, "print_screen"], ["ScrLk", 515, 5, 1, "scroll_lock"], ["Pause", 555, 5, 1, "pause"],
            # Row 2
            ["E/J", 5, 50, 1, "backtick"], ["1", 45, 50, 1, "1"], ["2", 85, 50, 1, "2"], ["3", 125, 50, 1, "3"], ["4", 165, 50, 1, "4"], 
            ["5", 205, 50, 1, "5"], ["6", 245, 50, 1, "6"], ["7", 285, 50, 1, "7"], ["8", 325, 50, 1, "8"], ["9", 365, 50, 1, "9"], ["0", 405, 50, 1, "0"],
            ["Ins", 475, 50, 1, "insert"], ["Home", 515, 50, 1, "home"], ["PgUp", 555, 50, 1, "page_up"],
            # Row 3 (QWERTY)
            ["Tab", 5, 90, 1.5, "tab"], ["Q", 65, 90, 1, "q"], ["W", 105, 90, 1, "w"], ["E", 145, 90, 1, "e"], ["R", 185, 90, 1, "r"], ["T", 225, 90, 1, "t"],
            ["Del", 475, 90, 1, "delete"], ["End", 515, 90, 1, "end"], ["PgDn", 555, 90, 1, "page_down"],
            # Row 4 (ASDF)
            ["Caps", 5, 130, 1.8, "caps_lock"], ["A", 77, 130, 1, "a"], ["S", 117, 130, 1, "s"], ["D", 157, 130, 1, "d"], ["F", 197, 130, 1, "f"],
            # Space & Arrows
            ["Space", 160, 210, 5, "space"], ["←", 475, 210, 1, "left"], ["↓", 515, 210, 1, "down"], ["→", 555, 210, 1, "right"],
        ]
        
        self.labels = {}
        self.setup_ui()
        
        # 設定ボタン（右上に配置）
        self.btn_settings = tk.Button(self.root, text="⚙", command=self.open_settings, bg="white", borderwidth=0)
        self.btn_settings.place(x=600*self.scale, y=5)

        # 監視
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def setup_ui(self):
        self.root.configure(bg="white")
        self.root.geometry(f"{int(610*self.scale)}x{int(260*self.scale)}")
        
        for text, x, y, w_mult, k_id in self.key_map:
            w, h = 38 * w_mult * self.scale, 38 * self.scale
            frame = tk.Frame(self.root, bg="white", highlightbackground="black", highlightthickness=1)
            frame.place(x=x*self.scale, y=y*self.scale, width=w, height=h)
            
            l1 = tk.Label(frame, text=text, bg="white", font=("Arial", int(8*self.scale), "bold"))
            l1.pack(expand=True)
            l2 = tk.Label(frame, text=str(self.stats.get(k_id, 0)), bg="white", fg="gray", font=("Arial", int(6*self.scale)))
            l2.pack(expand=True)
            
            self.labels[k_id] = (frame, l1, l2)

    def on_press(self, key):
        try:
            k_id = key.char.lower() if hasattr(key, 'char') else key.name.lower()
        except: return
        if k_id in self.labels:
            self.stats[k_id] = self.stats.get(k_id, 0) + 1
            self.root.after(0, self.flash_key, k_id)

    def flash_key(self, k_id):
        f, l1, l2 = self.labels[k_id]
        for w in [f, l1, l2]: w.config(bg="red")
        l2.config(text=str(self.stats[k_id]))
        self.root.after(150, lambda: self.reset_key(k_id))

    def reset_key(self, k_id):
        f, l1, l2 = self.labels[k_id]
        for w in [f, l1, l2]: w.config(bg="white")

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("設定")
        win.geometry("250x200")
        
        tk.Checkbutton(win, text="常に最前面", variable=tk.BooleanVar(value=self.config["topmost"]), 
                       command=lambda: self.update_config("topmost")).pack(pady=5)
        
        tk.Checkbutton(win, text="PC起動時に実行", variable=tk.BooleanVar(value=self.config["startup"]),
                       command=self.toggle_startup).pack(pady=5)
        
        tk.Label(win, text="画面サイズ").pack()
        scale_val = tk.DoubleVar(value=self.scale)
        scale_menu = ttk.Combobox(win, values=[0.5, 0.8, 1.0, 1.2, 1.5], textvariable=scale_val)
        scale_menu.pack()
        tk.Button(win, text="サイズ適用(要再起動)", command=lambda: self.update_config("scale", scale_val.get())).pack(pady=5)

    def update_config(self, key, value=None):
        if key == "topmost":
            self.config["topmost"] = not self.config["topmost"]
            self.root.attributes("-topmost", self.config["topmost"])
        else:
            self.config[key] = value
        self.save_json(CONFIG_FILE, self.config)

    def toggle_startup(self):
        self.config["startup"] = not self.config["startup"]
        self.save_json(CONFIG_FILE, self.config)
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg:
            if self.config["startup"]:
                winreg.SetValueEx(reg, APP_NAME, 0, winreg.REG_SZ, sys.executable)
            else:
                try: winreg.DeleteValue(reg, APP_NAME)
                except: pass

    def load_json(self, path, default={}):
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
        return default

    def save_json(self, path, data):
        with open(path, "w") as f: json.dump(data, f)

    def on_closing(self):
        self.save_json(STATS_FILE, self.stats)
        self.root.destroy()

if __name__ == "__main__":
    KeyCounterApp()
