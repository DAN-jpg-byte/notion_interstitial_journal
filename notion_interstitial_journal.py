import tkinter as tk
from tkinter import scrolledtext
import requests
import json
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

# 同一フォルダ内の pomodoro.py からクラスを読み込む
from pomodoro import PomodoroWindow

# .envファイルを読み込み
load_dotenv()

# --- 設定 ---
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

pomodoro_app = None

def send_to_notion():
    # 各入力欄からテキストを取得
    done_text = entry_done.get("1.0", tk.END).strip()
    goal_text = entry_goal.get("1.0", tk.END).strip()
    next_text = entry_next.get("1.0", tk.END).strip()
    mood_text = entry_mood.get("1.0", tk.END).strip()
    memo_text = entry_memo.get("1.0", tk.END).strip()

    # 現在の日時 (JST)
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(JST).isoformat()

    # Notion送信データの構築
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "title": {"title": [{"text": {"content": done_text}}]},
            "I%5BJp": {"date": {"start": current_time}},
            "qTOI": {"rich_text": [{"text": {"content": goal_text}}]},
            "udPY": {"rich_text": [{"text": {"content": next_text}}]},
            "cNJ%5C": {"rich_text": [{"text": {"content": mood_text}}]},
            "c%3BQ%7C": {"rich_text": [{"text": {"content": memo_text}}]}
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            log_time = datetime.now(JST).strftime('%H:%M:%S')
            output_box.insert(tk.END, f"[{log_time}] Notion送信成功！\n")
            
            # 入力欄をクリア
            for entry in [entry_done, entry_goal, entry_next, entry_mood, entry_memo]:
                entry.delete("1.0", tk.END)
            output_box.see(tk.END)
            return True
        else:
            output_box.insert(tk.END, f"エラー: {response.status_code}\n")
            output_box.see(tk.END)
            return False
    except Exception as e:
        output_box.insert(tk.END, f"通信エラー: {e}\n")
        output_box.see(tk.END)
        return False

# --- ポモドーロウィンドウを開く関数 ---
def open_pomodoro():
    global pomodoro_app
    # 親ウィンドウ(root)を渡して子ウィンドウを生成（既存があれば再利用）
    if pomodoro_app is None or not pomodoro_app.window.winfo_exists():
        pomodoro_app = PomodoroWindow(root)

def send_and_start_pomodoro():
    # Notion送信に成功した場合のみポモドーロを開始する
    success = send_to_notion()
    if not success:
        output_box.insert(tk.END, "Notion送信失敗のためポモドーロは開始しませんでした。\n")
        output_box.see(tk.END)
        return

    open_pomodoro()
    if pomodoro_app and not pomodoro_app.is_running:
        pomodoro_app.start_timer()

# --- GUI 構築 ---
root = tk.Tk()
root.title("Interstitail Journal & Pomodoro")
root.geometry("500x920")

PAD_Y = 5

# 各ラベルと入力エリアの配置
tk.Label(root, text="■ 終わったこと・完了したこと", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
entry_done = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_done.pack(pady=PAD_Y)

tk.Label(root, text="■ 始めたこと・次にやりたいこと", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
entry_next = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_next.pack(pady=PAD_Y)

tk.Label(root, text="■ 目的 ＆ 目標時間", font=("Helvetica", 10, "bold"), fg="#2E7D32").pack(pady=(10, 0))
entry_goal = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_goal.pack(pady=PAD_Y)

tk.Label(root, text="■ 気持ち", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
entry_mood = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=2)
entry_mood.pack(pady=PAD_Y)

tk.Label(root, text="■ メモ・後でやりたいこと", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
entry_memo = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
entry_memo.pack(pady=PAD_Y)

# 送信のみボタン
send_button = tk.Button(root, text="Notionに送信のみ", command=send_to_notion, 
                        width=25, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_button.pack(pady=10)

# 送信 + ポモドーロ開始ボタン
send_and_start_button = tk.Button(root, text="送信してポモドーロ開始", command=send_and_start_pomodoro,
                                  width=25, height=2, bg="#FF9800", fg="white", font=("Helvetica", 10, "bold"))
send_and_start_button.pack(pady=5)

# ポモドーロ起動ボタン（手動用）
pomodoro_button = tk.Button(root, text="⏱ ポモドーロタイマー起動", command=open_pomodoro, 
                           width=25, height=2, bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"))
pomodoro_button.pack(pady=5)

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
output_box.pack(pady=10)

# --- 起動時に自動でポモドーロを開く ---
open_pomodoro()

root.mainloop()