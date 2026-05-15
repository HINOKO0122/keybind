import tkinter as tk
from tkinter import ttk
import os
import json
import sys
import winreg
from pynput import keyboard

# --- 定数・パス設定 ---
APP_NAME = "RACEN_KeyCounter_Pro"
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
        self.config = self.load_json(CONFIG_FILE, default={
            "topmost": True, "scale": 1.0, "startup": False, "transparent": False
        })
        
        self.scale = self.config["scale"]
        self.labels = {}
        self.setup_window()
        self.define_keys()
        self.create_widgets()
        
        # 設定ボタン
        self.btn_settings = tk.Button(self.root, text="⚙", command=self.open_settings, bg="white", borderwidth=0, font=("Arial", 10))
        self.btn_settings.place(x=780*self.scale, y=5)

        # 監視
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def setup_window(self):
        self.root.geometry(f"{int(820*self.scale)}x{int(260*self.scale)}")
        self.apply_transparency()

    def apply_transparency(self):
        if self.config.get("transparent", False):
            self.root.config(bg="systemTransparent") # 一部OS用
            self.root.attributes("-transparentcolor", "white") # Windows用: 白を透明化
            self.root.attributes("-topmost", True)
        else:
            self.root.config(bg="white")
            self.root.attributes("-transparentcolor", "")
            self.root.attributes("-topmost", self.config["topmost"])

    def define_keys(self):
        s = 40 # 基本のキー間隔
        # [表示名, x, y, 横幅倍率, ID]
        self.key_map = [
            # Function Row
            ["Esc", 5, 5, 1, "esc"], ["F1", 75, 5, 1, "f1"], ["F2", 115, 5, 1, "f2"], ["F3", 155, 5, 1, "f3"], ["F4", 195, 5, 1, "f4"],
            ["F5", 255, 5, 1, "f5"], ["F6", 295, 5, 1, "f6"], ["F7", 335, 5, 1, "f7"], ["F8", 375, 5, 1, "f8"],
            ["F9", 435, 5, 1, "f9"], ["F10", 475, 5, 1, "f10"], ["F11", 515, 5, 1, "f11"], ["F12", 555, 5, 1, "f12"],
            ["PrtSc", 620, 5, 1, "print_screen"], ["ScrLk", 660, 5, 1, "scroll_lock"], ["Pause", 700, 5, 1, "pause"],
            
            # Number Row
            ["E/J", 5, 50, 1, "backtick"], ["1", 45, 50, 1, "1"], ["2", 85, 50, 1, "2"], ["3", 125, 50, 1, "3"], ["4", 165, 50, 1, "4"], 
            ["5", 205, 50, 1, "5"], ["6", 245, 50, 1, "6"], ["7", 285, 50, 1, "7"], ["8", 325, 50, 1, "8"], ["9", 365, 50, 1, "9"], ["0", 405, 50, 1, "0"],
            ["-", 445, 50, 1, "-"], ["^", 485, 50, 1, "="], ["￥", 525, 50, 1, "intl_backsl"], ["BS", 565, 1.4, 1, "backspace"],
            ["Ins", 620, 50, 1, "insert"], ["Home", 660, 50, 1, "home"], ["PgUp", 700, 50, 1, "page_up"],

            # QWERTY Row
            ["Tab", 5, 90, 1.5, "tab"], ["Q", 65, 90, 1, "q"], ["W", 105, 90, 1, "w"], ["E", 145, 90, 1, "e"], ["R", 185, 90, 1, "r"], ["T", 225, 90, 1, "t"],
            ["Y", 265, 90, 1, "y"], ["U", 305, 90, 1, "u"], ["I", 345, 90, 1, "i"], ["O", 385, 90, 1, "o"], ["P", 425, 90, 1, "p"], ["@", 465, 90, 1, "["],
            ["[", 505, 90, 1, "]"], ["Ent", 555, 90, 1.4, "enter"], 
            ["Del", 620, 90, 1, "delete"], ["End", 660, 90, 1, "end"], ["PgDn", 700, 90, 1, "page_down"],

            # ASDF Row
            ["Caps", 5, 130, 1.8, "caps_lock"], ["A", 77, 130, 1, "a"], ["S", 117, 130, 1, "s"], ["D", 157, 130, 1, "d"], ["F", 197, 130, 1, "f"],
            ["G", 237, 130, 1, "g"], ["H", 277, 130, 1, "h"], ["J", 317, 130, 1, "j"], ["K", 357, 130, 1, "k"], ["L", 397, 130, 1, "l"], [";", 437, 130, 1, ";"],
            [":", 477, 130, 1, "'"], ["]", 517, 130, 1, "\\"],

            # ZXCV Row
            ["Shift", 5, 170, 2.2, "shift"], ["Z", 93, 170, 1, "z"], ["X", 133, 170, 1, "x"], ["C", 173, 170, 1, "c"], ["V", 213, 170, 1, "v"],
            ["B", 253, 170, 1, "b"], ["N", 293, 170, 1, "n"], ["M", 333, 170, 1, "m"], [",", 373, 170, 1, ","], [".", 413, 170, 1, "."],
            ["/", 453, 170, 1, "/"], ["_", 493, 170, 1, "intl_ro"], ["Shift", 533, 1.8, 1, "shift_r"], ["↑", 660, 170, 1, "up"],

            # Bottom Row
            ["Ctrl", 5, 210, 1.2, "ctrl_l"], ["Win", 55, 210, 1.2, "cmd"], ["Alt", 105, 210, 1.2, "alt_l"], ["Space", 155, 210, 5, "space"],
            ["Kana", 355, 210, 1.2, "lang1"], ["Fn", 405, 210, 1.2, "fn"], ["APP", 455, 210, 1.2, "menu"], ["Ctrl", 505, 210, 1.2, "ctrl_r"],
            ["←", 620, 210, 1, "left"], ["↓", 660, 210, 1, "down"], ["→", 700, 210, 1, "right"],
        ]

    def create_widgets(self):
        for text, x, y, w_mult, k_id in self.key_map:
            w, h = 38 * w_mult * self.scale, 38 * self.scale
            frame = tk.Frame(self.root, bg="white", highlightbackground="black", highlightthickness=1)
            frame.place(x=x*self.scale, y=y*self.scale, width=w, height=h)
            
            l1 = tk.Label(frame, text=text, bg="white", font=("Arial", int(7*self.scale), "bold"))
            l1.pack(expand=True)
            l2 = tk.Label(frame, text=str(self.stats.get(k_id, 0)), bg="white", fg="gray", font=("Arial", int(5*self.scale)))
            l2.pack(expand=True)
            self.labels[k_id] = (frame, l1, l2)

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char: k_id = key.char.lower()
            else: k_id = key.name.lower()
        except: return
        if k_id in self.labels:
            self.stats[k_id] = self.stats.get(k_id, 0) + 1
            self.root.after(0, self.flash_key, k_id)

    def flash_key(self, k_id):
        f, l1, l2 = self.labels[k_id]
        for w in [f, l1, l2]: w.config(bg="red")
        l2.config(text=str(self.stats[k_id]))
        self.root.after(100, lambda: self.reset_key(k_id))

    def reset_key(self, k_id):
        f, l1, l2 = self.labels[k_id]
        bg_col = "white"
        for w in [f, l1, l2]: w.config(bg=bg_col)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("300x250")
        
        tk.Checkbutton(win, text="常に最前面", variable=tk.BooleanVar(value=self.config["topmost"]), 
                       command=lambda: self.update_config("topmost")).pack(pady=5)
        
        tk.Checkbutton(win, text="背景を透過 (白を消す)", variable=tk.BooleanVar(value=self.config["transparent"]),
                       command=lambda: self.update_config("transparent")).pack(pady=5)
        
        tk.Checkbutton(win, text="PC起動時に実行", variable=tk.BooleanVar(value=self.config["startup"]),
                       command=self.toggle_startup).pack(pady=5)
        
        tk.Label(win, text="画面サイズ (要再起動)").pack()
        scale_val = tk.DoubleVar(value=self.scale)
        scale_menu = ttk.Combobox(win, values=[0.5, 0.8, 1.0, 1.2, 1.5], textvariable=scale_val)
        scale_menu.pack()
        tk.Button(win, text="適用", command=lambda: self.update_config("scale", scale_val.get())).pack(pady=10)

    def update_config(self, key, value=None):
        if value is None: self.config[key] = not self.config[key]
        else: self.config[key] = value
        self.save_json(CONFIG_FILE, self.config)
        if key in ["topmost", "transparent"]: self.apply_transparency()

    def toggle_startup(self):
        self.config["startup"] = not self.config["startup"]
        self.save_json(CONFIG_FILE, self.config)
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key, 0, winreg.KEY_SET_VALUE) as reg:
            if self.config["startup"]: winreg.SetValueEx(reg, APP_NAME, 0, winreg.REG_SZ, sys.executable)
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
