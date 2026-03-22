import os
import requests
import tkinter as tk
import subprocess
import threading
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

# --- 設定 ---
WIFI_INTERFACE_NAME = "Wi-Fi 2"

WORK_TIME = 25 * 60  # 25分
BREAK_TIME = 5 * 60   # 5分


# #テスト用　普段はコメントアウト
# WORK_TIME = 10  # 10秒
# BREAK_TIME = 10   # 10秒
# # --------------------------



NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

class PomodoroWindow:
    def __init__(self, parent):
        # メインウィンドウ(parent)を親に持つ新しいウィンドウを作成
        self.window = tk.Toplevel(parent)
        self.window.title("Pomodoro Timer")
        self.window.geometry("350x320")
        
        # ウィンドウが閉じられた時にタイマーを止める設定
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.cycle_count = 0
        self.is_running = False
        self.stop_event = threading.Event() # スレッド停止用フラグ

        # UIの配置
        self.label_status = tk.Label(self.window, text="待機中", font=("MS Gothic", 12))
        self.label_status.pack(pady=10)
        
        self.label_count = tk.Label(self.window, text=f"完了回数: {self.cycle_count}", font=("MS Gothic", 12, "bold"), fg="#2ecc71")
        self.label_count.pack(pady=5)

        self.label_timer = tk.Label(self.window, text="25:00", font=("Helvetica", 48))
        self.label_timer.pack(pady=10)
        
        self.btn_start = tk.Button(self.window, text="集中開始", command=self.start_timer, width=15, height=2)
        self.btn_start.pack(pady=10)

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
                "title": {"title": [{"text": {"content": f"作業中断しました ({self.cycle_count}回目)"}}]},
                "I%5BJp": {"date": {"start": current_time}},
                "udPY": {"rich_text": [{"text": {"content": "ポモドーロー休憩スタート"}}]},
                "c%3BQ%7C": {"rich_text": [{"text": {"content": f"ポモドーロー {self.cycle_count} 回目のサイクルです"}}]}
            }
        }
        try:
            response = requests.post(NOTION_API_URL, headers=headers, json=data)
            if response.status_code == 200:
                print(f"Notion記録成功 ({self.cycle_count}回目)")
        except Exception as e:
            print(f"エラー発生: {e}")

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
            # --- 集中終了直後の処理 ---
            self.cycle_count += 1
            self.label_count.config(text=f"完了回数: {self.cycle_count}")
            self.label_status.config(text="📡 Notionへ自動記録中...")
            self.post_to_notion()
            
            # 2. Wi-Fi切断
            self.set_wifi(False)
            
            # 3. 休憩時間 (5分)
            if self.run_countdown(BREAK_TIME, "☕ 休憩中 (通信OFF)"):
                # 4. Wi-Fi復帰
                self.set_wifi(True)
                self.label_status.config(text=f"{self.cycle_count}セット完了！")
        
        self.btn_start.config(state="normal")
        self.is_running = False

    def run_countdown(self, seconds, status_text):
        """カウントダウン実行（途中で閉じられたらFalseを返す）"""
        self.label_status.config(text=status_text)
        while seconds >= 0:
            if self.stop_event.is_set():
                return False
            mins, secs = divmod(seconds, 60)
            self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            seconds -= 1
        return True

    def on_closing(self):
        """ウィンドウが閉じられた時の処理"""
        self.stop_event.set()
        self.window.destroy()

if __name__ == "__main__":
    # 単体で動かしたい時用
    root = tk.Tk()
    app = PomodoroWindow(root)
    root.mainloop()