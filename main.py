import tkinter as tk
import os
import json
from pynput import keyboard
from threading import Thread

# --- 設定とデータ保存パス ---
APP_NAME = "MyKeyCounter"
DATA_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class KeyCounterApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Key Counter")
        self.root.configure(bg="white")
        
        # データの読み込み
        self.stats = self.load_data(STATS_FILE)
        self.config = self.load_data(CONFIG_FILE, default={"topmost": True, "scale": 1.0})
        
        self.root.attributes("-topmost", self.config.get("topmost", True))
        
        # キーボードレイアウト定義（簡易版：ここを増やして写真に近づけます）
        # [表示名, x座標, y座標, キー名]
        self.key_map = [
            ["Esc", 0, 0, "esc"], ["F1", 50, 0, "f1"], ["F2", 80, 0, "f2"],
            ["Q", 0, 40, "q"], ["W", 40, 40, "w"], ["E", 80, 40, "e"],
            ["A", 0, 80, "a"], ["S", 40, 80, "s"], ["D", 80, 80, "d"],
            ["Space", 80, 160, "space"]
        ]
        
        self.labels = {}
        self.create_widgets()
        
        # 入力監視スタート
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def create_widgets(self):
        for text, x, y, k_id in self.key_map:
            count = self.stats.get(k_id, 0)
            frame = tk.Frame(self.root, bg="white", highlightbackground="black", highlightthickness=1)
            frame.place(x=x, y=y, width=38, height=38)
            
            main_label = tk.Label(frame, text=text, bg="white", fg="black", font=("Arial", 8, "bold"))
            main_label.pack()
            
            count_label = tk.Label(frame, text=str(count), bg="white", fg="gray", font=("Arial", 6))
            count_label.pack()
            
            self.labels[k_id] = (frame, main_label, count_label)

    def on_press(self, key):
        try:
            k_id = key.char.lower() if hasattr(key, 'char') else key.name.lower()
        except:
            return

        if k_id in self.labels:
            # カウント更新
            self.stats[k_id] = self.stats.get(k_id, 0) + 1
            
            # UI更新（スレッドセーフに）
            self.root.after(0, self.update_ui, k_id)

    def update_ui(self, k_id):
        frame, main_l, count_l = self.labels[k_id]
        # 赤くする
        frame.config(bg="red")
        main_l.config(bg="red")
        count_l.config(bg="red", text=str(self.stats[k_id]))
        # 100ms後に白に戻す
        self.root.after(100, lambda: self.reset_color(k_id))

    def reset_color(self, k_id):
        frame, main_l, count_l = self.labels[k_id]
        frame.config(bg="white")
        main_l.config(bg="white")
        count_l.config(bg="white")

    def load_data(self, path, default={}):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return default

    def on_closing(self):
        with open(STATS_FILE, "w") as f:
            json.dump(self.stats, f)
        self.root.destroy()

if __name__ == "__main__":
    KeyCounterApp()
