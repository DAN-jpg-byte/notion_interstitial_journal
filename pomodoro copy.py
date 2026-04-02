import tkinter as tk
from tkinter import scrolledtext
import requests
import json
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
# 子ウィンドウのクラスをインポート
from pomodoro import PomodoroWindow

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def send_to_notion():
    done_text = entry_done.get("1.0", tk.END).strip()
    goal_text = entry_goal.get("1.0", tk.END).strip()
    next_text = entry_next.get("1.0", tk.END).strip()
    mood_text = entry_mood.get("1.0", tk.END).strip()
    memo_text = entry_memo.get("1.0", tk.END).strip()

    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(JST).isoformat()

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
            for entry in [entry_done, entry_goal, entry_next, entry_mood, entry_memo]:
                entry.delete("1.0", tk.END)
            output_box.see(tk.END)
        else:
            output_box.insert(tk.END, f"エラー: {response.status_code}\n")
    except Exception as e:
        output_box.insert(tk.END, f"通信エラー: {e}\n")

# --- ポモドーロウィンドウを開く関数 ---
def open_pomodoro():
    # Toplevelとしてタイマーを起動
    PomodoroWindow(root)

# --- GUI 構築 ---
root = tk.Tk()
root.title("Journal & Pomodoro")
root.geometry("500x920")

PAD_Y = 5

# ジャーナル入力項目（既存）
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

tk.Label(root, text="■ メモ", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
entry_memo = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
entry_memo.pack(pady=PAD_Y)

# ボタンエリア
send_button = tk.Button(root, text="Notionに送信", command=send_to_notion, 
                        width=25, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_button.pack(pady=10)

# ポモドーロ起動ボタン
pomodoro_button = tk.Button(root, text="⏱ ポモドーロタイマー起動", command=open_pomodoro, 
                           width=25, height=2, bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"))
pomodoro_button.pack(pady=5)

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
output_box.pack(pady=10)

root.mainloop()