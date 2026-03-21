import os
import requests
import tkinter as tk
import subprocess
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

# .env読み込み
load_dotenv()

# --- 設定 ---
WIFI_INTERFACE_NAME = "Wi-Fi 2"
# テスト用設定
WORK_TIME = 10
BREAK_TIME = 10

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

class PomodoroWifiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro & Notion Auto-Log")
        self.root.geometry("350x300")
        
        self.cycle_count = 0
        
        self.label_status = tk.Label(root, text="待機中", font=("MS Gothic", 12))
        self.label_status.pack(pady=10)
        
        self.label_count = tk.Label(root, text=f"完了回数: {self.cycle_count}", font=("MS Gothic", 12, "bold"), fg="#2ecc71")
        self.label_count.pack(pady=5)

        self.label_timer = tk.Label(root, text="25:00", font=("Helvetica", 48))
        self.label_timer.pack(pady=10)
        
        self.btn_start = tk.Button(root, text="集中開始", command=self.start_timer, width=15, height=2)
        self.btn_start.pack(pady=10)

        self.is_running = False

    def post_to_notion(self):
        """Notionに自動でログを送信する"""
        current_time = datetime.now().isoformat()
        
        headers = {
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # すでにカウントアップされた self.cycle_count を使用します
        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "title": {"title": [{"text": {"content": f"作業中断しました ({self.cycle_count}回目)"}}]},
                "I%5BJp": {"date": {"start": current_time}},
                "qTOI": {"rich_text": [{"text": {"content": ""}}]},
                "udPY": {"rich_text": [{"text": {"content": "ポモドーロー休憩スタート"}}]},
                "cNJ%5C": {"rich_text": [{"text": {"content": ""}}]},
                "c%3BQ%7C": {"rich_text": [{"text": {"content": f"ポモドーロー {self.cycle_count} 回目のサイクルです"}}]}
            }
        }
        
        try:
            response = requests.post(NOTION_API_URL, headers=headers, json=data)
            if response.status_code == 200:
                print(f"Notion記録成功 ({self.cycle_count}回目)")
            else:
                print(f"Notion記録失敗: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"エラー発生: {e}")

    def set_wifi(self, enable):
        state = "enabled" if enable else "disabled"
        subprocess.run(f'netsh interface set interface "{WIFI_INTERFACE_NAME}" admin={state}', shell=True)

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.config(state="disabled")
            threading.Thread(target=self.pomodoro_cycle, daemon=True).start()

    def pomodoro_cycle(self):
        # 1. 集中時間 (25分)
        self.run_countdown(WORK_TIME, "🔥 集中中...")
        
        # --- 集中終了直後の処理 ---
        
        # まずカウントを1増やす
        self.cycle_count += 1
        # UIの表示を更新
        self.label_count.config(text=f"完了回数: {self.cycle_count}")
        
        # Notionへ送信（増えた後のカウントで記録される）
        self.label_status.config(text="📡 Notionへ自動記録中...")
        self.post_to_notion()
        
        # 2. Wi-Fi切断（強制休憩開始）
        self.set_wifi(False)
        
        # 3. 休憩時間 (5分)
        self.run_countdown(BREAK_TIME, "☕ 休憩中 (通信OFF)")
        
        # 4. Wi-Fi復帰
        self.set_wifi(True)
        
        self.label_status.config(text=f"{self.cycle_count}セット完了！")
        self.btn_start.config(state="normal")
        self.is_running = False

    def run_countdown(self, seconds, status_text):
        self.label_status.config(text=status_text)
        while seconds >= 0:
            mins, secs = divmod(seconds, 60)
            self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
            self.root.update()
            time.sleep(1)
            seconds -= 1

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroWifiApp(root)
    root.mainloop()