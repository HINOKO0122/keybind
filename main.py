import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import sys
import winreg
from pynput import keyboard

APP_NAME = "RACEN_KeyCounter_V5"
DATA_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class KeyCounterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KeyCounter")
        
        self.stats = self.load_json(STATS_FILE)
        self.config = self.load_json(CONFIG_FILE, default={
            "topmost": True, "scale": 1.0, "startup": False, "transparent": False
        })
        
        self.scale = self.config["scale"]
        self.labels = {}
        self.settings_window = None
        
        self.setup_window()
        self.create_widgets()
        
        # ⚙ボタン
        self.btn_settings = tk.Button(self.root, text="⚙", command=self.open_settings, bg="white", borderwidth=1)
        self.btn_settings.place(x=785*self.scale, y=5)

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def setup_window(self):
        # 画面中央に配置
        w, h = int(820*self.scale), int(260*self.scale)
        self.root.geometry(f"{w}x{h}")
        self.apply_transparency()

    def apply_transparency(self):
        if self.config.get("transparent", False):
            self.root.config(bg="gray") 
            self.root.attributes("-transparentcolor", "gray")
            self.root.attributes("-topmost", True)
        else:
            self.root.config(bg="white")
            self.root.attributes("-transparentcolor", "")
            self.root.attributes("-topmost", self.config["topmost"])

    def create_widgets(self):
        # 既存のボタンを消去（サイズ変更時用）
        for widget in self.root.winfo_children():
            if widget != self.btn_settings:
                widget.destroy()

        keys = [
            ["Esc", 5, 5, 1.0, "esc"], ["F1", 75, 5, 1.0, "f1"], ["F2", 115, 5, 1.0, "f2"], ["F3", 155, 5, 1.0, "f3"], ["F4", 195, 5, 1.0, "f4"],
            ["F5", 255, 5, 1.0, "f5"], ["F6", 295, 5, 1.0, "f6"], ["F7", 335, 5, 1.0, "f7"], ["F8", 375, 5, 1.0, "f8"],
            ["F9", 435, 5, 1.0, "f9"], ["F10", 475, 5, 1.0, "f10"], ["F11", 515, 5, 1.0, "f11"], ["F12", 555, 5, 1.0, "f12"],
            ["PrtSc", 620, 5, 1.0, "print_screen"], ["ScrLk", 660, 5, 1.0, "scroll_lock"], ["Pause", 700, 5, 1.0, "pause"],
            ["半/全", 5, 50, 1.0, "backtick"], ["1", 45, 50, 1.0, "1"], ["2", 85, 50, 1.0, "2"], ["3", 125, 50, 1.0, "3"], ["4", 165, 50, 1.0, "4"], 
            ["5", 205, 50, 1.0, "5"], ["6", 245, 50, 1.0, "6"], ["7", 285, 50, 1.0, "7"], ["8", 325, 50, 1.0, "8"], ["9", 365, 50, 1.0, "9"], ["0", 405, 50, 1.0, "0"],
            ["-", 445, 50, 1.0, "-"], ["^", 485, 50, 1.0, "equal"], ["¥", 525, 50, 1.0, "intl_backslash"], ["BS", 565, 50, 1.4, "backspace"],
            ["Ins", 620, 50, 1.0, "insert"], ["Home", 660, 50, 1.0, "home"], ["PgUp", 700, 50, 1.0, "page_up"],
            ["Tab", 5, 90, 1.5, "tab"], ["Q", 65, 90, 1.0, "q"], ["W", 105, 90, 1.0, "w"], ["E", 145, 90, 1.0, "e"], ["R", 185, 90, 1.0, "r"], ["T", 225, 90, 1.0, "t"],
            ["Y", 265, 90, 1.0, "y"], ["U", 305, 90, 1.0, "u"], ["I", 345, 90, 1.0, "i"], ["O", 385, 90, 1.0, "o"], ["P", 425, 90, 1.0, "p"], ["@", 465, 90, 1.0, "bracket_left"],
            ["[", 505, 90, 1.0, "bracket_right"], ["Enter", 555, 90, 1.4, "enter"], 
            ["Del", 620, 90, 1.0, "delete"], ["End", 660, 90, 1.0, "end"], ["PgDn", 700, 90, 1.0, "page_down"],
            ["Caps", 5, 130, 1.8, "caps_lock"], ["A", 77, 130, 1.0, "a"], ["S", 117, 130, 1.0, "s"], ["D", 157, 130, 1.0, "d"], ["F", 197, 130, 1.0, "f"],
            ["G", 237, 130, 1.0, "g"], ["H", 277, 130, 1.0, "h"], ["J", 317, 130, 1.0, "j"], ["K", 357, 130, 1.0, "k"], ["L", 397, 130, 1.0, "l"], [";", 437, 130, 1.0, "semicolon"],
            [":", 477, 130, 1.0, "apostrophe"], ["]", 517, 130, 1.0, "backslash"],
            ["Shift", 5, 170, 2.2, "shift"], ["Z", 93, 170, 1.0, "z"], ["X", 133, 170, 1.0, "x"], ["C", 173, 170, 1.0, "c"], ["V", 213, 170, 1.0, "v"],
            ["B", 253, 170, 1.0, "b"], ["N", 293, 170, 1.0, "n"], ["M", 333, 170, 1.0, "m"], [",", 373, 170, 1.0, "comma"], [".", 413, 170, 1.0, "period"],
            ["/", 453, 170, 1.0, "slash"], ["ろ", 493, 170, 1.0, "intl_ro"], ["Shift", 533, 170, 1.8, "shift_r"], ["↑", 660, 170, 1.0, "up"],
            ["Ctrl", 5, 210, 1.2, "ctrl_l"], ["Win", 55, 210, 1.2, "cmd"], ["Alt", 105, 210, 1.2, "alt_l"], ["無変換", 155, 210, 1.2, "convert"],
            ["Space", 205, 210, 3.5, "space"], ["変換", 345, 210, 1.2, "non_convert"], ["かな", 395, 210, 1.2, "lang1"], ["Ctrl", 445, 210, 1.2, "ctrl_r"],
            ["←", 620, 210, 1.0, "left"], ["↓", 660, 210, 1.0, "down"], ["→", 700, 210, 1.0, "right"],
        ]

        for item in keys:
            text, x, y, w_mult, k_id = item
            w, h = 38 * w_mult * self.scale, 38 * self.scale
            f = tk.Frame(self.root, bg="white", highlightbackground="black", highlightthickness=1)
            f.place(x=x*self.scale, y=y*self.scale, width=w, height=h)
            l1 = tk.Label(f, text=text, bg="white", font=("Arial", int(7*self.scale), "bold"))
            l1.pack(expand=True)
            l2 = tk.Label(f, text=str(self.stats.get(k_id, 0)), bg="white", fg="gray", font=("Arial", int(5*self.scale)))
            l2.pack(expand=True)
            self.labels[k_id] = (f, l1, l2)
        
        # ⚙ボタンを最前面に
        self.btn_settings.lift()
        self.btn_settings.place(x=785*self.scale, y=5)

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char: k_id = key.char.lower()
            else: k_id = str(key).replace("Key.", "").lower()
        except: return
        if k_id in self.labels:
            self.stats[k_id] = self.stats.get(k_id, 0) + 1
            self.root.after(0, self.flash, k_id)

    def flash(self, k_id):
        f, l1, l2 = self.labels[k_id]
        for w in [f, l1, l2]: w.config(bg="red")
        l2.config(text=str(self.stats[k_id]))
        self.root.after(100, lambda: self.reset(k_id))

    def reset(self, k_id):
        if k_id in self.labels:
            f, l1, l2 = self.labels[k_id]
            for w in [f, l1, l2]: w.config(bg="white")

    def open_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("設定")
        self.settings_window.geometry("300x380")
        
        def add_toggle(label_text, config_key, extra_action=None):
            f = tk.Frame(self.settings_window)
            f.pack(pady=10, fill="x", padx=20)
            tk.Label(f, text=label_text).pack(side="left")
            btn = tk.Button(f, text="ON" if self.config[config_key] else "OFF", width=8)
            def cmd():
                self.config[config_key] = not self.config[config_key]
                btn.config(text="ON" if self.config[config_key] else "OFF")
                self.save_json(CONFIG_FILE, self.config)
                if extra_action: extra_action()
                self.apply_transparency()
            btn.config(command=cmd)
            btn.pack(side="right")

        add_toggle("常に最前面：", "topmost")
        add_toggle("背景透過：", "transparent")
        add_toggle("自動起動：", "startup", self.toggle_startup)

        tk.Label(self.settings_window, text="--- サイズ変更 ---").pack(pady=10)
        sc = tk.DoubleVar(value=self.scale)
        combo = ttk.Combobox(self.settings_window, values=[0.5, 0.8, 1.0, 1.2, 1.5], textvariable=sc, state="readonly")
        combo.pack(pady=5)
        
        def update_size():
            self.scale = sc.get()
            self.config["scale"] = self.scale
            self.save_json(CONFIG_FILE, self.config)
            self.setup_window()
            self.create_widgets()
            messagebox.showinfo("反映", "サイズを変更しました。")

        tk.Button(self.settings_window, text="サイズを即座に適用", command=update_size).pack(pady=20)

    def toggle_startup(self):
        key = winreg.HKEY_CURRENT_USER
        sub = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, sub, 0, winreg.KEY_SET_VALUE) as r:
            if self.config["startup"]:
                winreg.SetValueEx(r, APP_NAME, 0, winreg.REG_SZ, sys.executable)
            else:
                try: winreg.DeleteValue(r, APP_NAME)
                except: pass

    def load_json(self, path, default={}):
        if os.path.exists(path):
            try:
                with open(path, "r") as f: return json.load(f)
            except: pass
        return default

    def save_json(self, path, data):
        with open(path, "w") as f: json.dump(data, f)

    def on_closing(self):
        self.save_json(STATS_FILE, self.stats)
        self.root.destroy()

if __name__ == "__main__":
    KeyCounterApp()
