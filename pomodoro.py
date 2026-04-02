import os
import requests
import tkinter as tk
import subprocess
import threading
import time
import random
from PIL import Image, ImageTk # pip install Pillow が必要です
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- 設定 ---
WIFI_INTERFACE_NAME = "Wi-Fi 2"
WORK_TIME = 25 * 60  # 25分
BREAK_TIME = 5 * 60   # 5分




# # # --- テスト用普段はコメントアウト ---
# WORK_TIME = 10  
# BREAK_TIME = 10  


IMAGE_FOLDER = "pomodoro_images"

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

class PomodoroWindow:
    def __init__(self, parent):
        # メインウィンドウの設定
        self.window = tk.Toplevel(parent)
        self.window.title("Pomodoro Timer")
        self.window.geometry("350x320")
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.cycle_count = 0
        self.is_running = False
        self.stop_event = threading.Event()
        self.fs_window = None # フルスクリーンウィンドウ用

        # UIの配置
        self.label_status = tk.Label(self.window, text="待機中", font=("MS Gothic", 12))
        self.label_status.pack(pady=10)
        
        self.label_count = tk.Label(self.window, text=f"完了回数: {self.cycle_count}", font=("MS Gothic", 12, "bold"), fg="#2ecc71")
        self.label_count.pack(pady=5)

        self.label_timer = tk.Label(self.window, text="25:00", font=("Helvetica", 48))
        self.label_timer.pack(pady=10)
        
        # ボタンのデザインを元に戻しました
        self.btn_start = tk.Button(self.window, text="集中開始", command=self.start_timer, width=15, height=2)
        self.btn_start.pack(pady=10)

    def show_fullscreen_image(self):
        """画像を全画面で表示し、クリックやEscで閉じれるようにする"""
        try:
            if not os.path.exists(IMAGE_FOLDER):
                return
                
            valid_extensions = ('.jpg', '.jpeg', '.png')
            images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_extensions)]
            
            if not images:
                return

            img_path = os.path.join(IMAGE_FOLDER, random.choice(images))

            # フルスクリーンウィンドウの作成
            self.fs_window = tk.Toplevel(self.window)
            self.fs_window.attributes("-fullscreen", True)
            self.fs_window.attributes("-topmost", True)
            self.fs_window.config(bg="black")

            screen_w = self.fs_window.winfo_screenwidth()
            screen_h = self.fs_window.winfo_screenheight()

            img = Image.open(img_path)
            img.thumbnail((screen_w, screen_h), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.fs_window, image=self.photo, bg="black")
            lbl.pack(expand=True)

            # 手動で閉じるためのバインド
            lbl.bind("<Button-1>", lambda e: self.close_fullscreen_image())
            self.fs_window.bind("<Button-1>", lambda e: self.close_fullscreen_image())
            self.fs_window.bind("<Escape>", lambda e: self.close_fullscreen_image())
            
        except Exception as e:
            print(f"画像表示エラー: {e}")

    def close_fullscreen_image(self):
        """全画面ウィンドウを安全に閉じる"""
        if self.fs_window:
            self.fs_window.destroy()
            self.fs_window = None

    def post_to_notion(self):
        """Notionに自動でログを送信する"""
        JST = timezone(timedelta(hours=+9), 'JST')
        current_time = datetime.now(JST).isoformat()
        headers = {
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "title": {"title": [{"text": {"content": f"作業中断しました ({self.cycle_count}回目のポモドーロ完了)"}}]},
                "I%5BJp": {"date": {"start": current_time}},
                "udPY": {"rich_text": [{"text": {"content": "ポモドーロー休憩スタート"}}]},
                "c%3BQ%7C": {"rich_text": [{"text": {"content": f"ポモドーロー {self.cycle_count} 回目のサイクルです"}}]}
            }
        }
        try:
            response = requests.post(NOTION_API_URL, headers=headers, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Notionエラー: {e}")
            return False

    def set_wifi(self, enable):
        state = "enabled" if enable else "disabled"
        subprocess.run(f'netsh interface set interface "{WIFI_INTERFACE_NAME}" admin={state}', shell=True)

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.btn_start.config(state="disabled")
            threading.Thread(target=self.pomodoro_cycle, daemon=True).start()

    def pomodoro_cycle(self):
        # 1. 集中時間 (25分)
        if self.run_countdown(WORK_TIME, "🔥 集中中..."):
            
            # 集中終了後のステータス更新
            self.cycle_count += 1
            self.window.after(0, lambda: self.label_count.config(text=f"完了回数: {self.cycle_count}"))
            self.window.after(0, lambda: self.label_status.config(text="📡 Notionへ自動記録中..."))
            
            # Notionへ送信
            success = self.post_to_notion()
            
            if success:
                self.window.after(0, lambda: self.label_status.config(text="✅ Notion記録成功！休憩開始"))
            else:
                self.window.after(0, lambda: self.label_status.config(text="❌ Notion記録失敗...休憩開始"))

            # 2. Wi-Fi切断 & 全画面画像表示
            self.set_wifi(False)
            self.window.after(0, self.show_fullscreen_image)
            
            # 3. 休憩時間 (5分)
            if self.run_countdown(BREAK_TIME, "☕ 休憩中 (通信OFF)"):
                # 4. Wi-Fi復帰 & 全画面解除
                self.set_wifi(True)
                self.window.after(0, self.close_fullscreen_image)
                self.window.after(0, lambda: self.label_status.config(text=f"{self.cycle_count}セット完了！"))
        
        self.btn_start.config(state="normal")
        self.is_running = False

    def run_countdown(self, seconds, status_text):
        self.window.after(0, lambda: self.label_status.config(text=status_text))
        while seconds >= 0:
            if self.stop_event.is_set():
                return False
            mins, secs = divmod(seconds, 60)
            self.window.after(0, lambda m=mins, s=secs: self.label_timer.config(text=f"{m:02d}:{s:02d}"))
            time.sleep(1)
            seconds -= 1
        return True

    def on_closing(self):
        self.close_fullscreen_image()
        self.stop_event.set()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroWindow(root)
    root.mainloop()