import tkinter as tk
from tkinter import scrolledtext
import requests
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os

# .envファイルを読み込み
load_dotenv()

# --- 設定 ---
NOTION_API_TOKEN  = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def send_to_notion():
    # 1. 各入力欄からテキストを取得
    done_text = entry_done.get("1.0", tk.END).strip()
    goal_text = entry_goal.get("1.0", tk.END).strip()      # 【追加】目的
    next_text = entry_next.get("1.0", tk.END).strip()
    mood_text = entry_mood.get("1.0", tk.END).strip()
    memo_text = entry_memo.get("1.0", tk.END).strip()

    # 2. 現在の日時
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(JST).isoformat()

    # 3. Notion送信データの構築
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "title": {"title": [{"text": {"content": done_text}}]},
            "I%5BJp": {"date": {"start": current_time}},
            # 【追加】「目的」のID: qTOI
            "qTOI": {
                "rich_text": [{"text": {"content": goal_text}}]
            },
            "udPY": {"rich_text": [{"text": {"content": next_text}}]},
            "cNJ%5C": {"rich_text": [{"text": {"content": mood_text}}]},
            "c%3BQ%7C": {"rich_text": [{"text": {"content": memo_text}}]}
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            log_time = datetime.now(JST).strftime('%H:%M:%S')
            output_box.insert(tk.END, f"[{log_time}] 送信成功！\n")
            
            # 入力欄をクリア（goalも追加）
            entry_done.delete("1.0", tk.END)
            entry_goal.delete("1.0", tk.END)
            entry_next.delete("1.0", tk.END)
            entry_mood.delete("1.0", tk.END)
            entry_memo.delete("1.0", tk.END)
            output_box.see(tk.END)
        else:
            output_box.insert(tk.END, f"エラー: {response.status_code}\n")
            output_box.see(tk.END)
    except Exception as e:
        output_box.insert(tk.END, f"通信エラー: {e}\n")

# --- GUI ---
root = tk.Tk()
root.title("インタースティシャル・ジャーナリング")
root.geometry("500x850") # 項目が増えたので高さを少し広げました

PAD_Y = 5

# ■ 完了したこと
label_done = tk.Label(root, text="■ 終わったこと・完了したこと ", font=("Helvetica", 10, "bold"))
label_done.pack(pady=(10, 0))
entry_done = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_done.pack(pady=PAD_Y)



# ■ 次にやりたいこと
label_next = tk.Label(root, text="■ 始めたこと・次にやりたいこと", font=("Helvetica", 10, "bold"))
label_next.pack(pady=(10, 0))
entry_next = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_next.pack(pady=PAD_Y)


# 【追加】■ 目的 (qTOI)
label_goal = tk.Label(root, text="■ 目的", font=("Helvetica", 10, "bold"), fg="#2E7D32")
label_goal.pack(pady=(10, 0))
entry_goal = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_goal.pack(pady=PAD_Y)



# ■ 気持ち / メモ (以下略)
label_mood = tk.Label(root, text="■ 気持ち", font=("Helvetica", 10, "bold"))
label_mood.pack(pady=(10, 0))
entry_mood = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=2)
entry_mood.pack(pady=PAD_Y)

label_memo = tk.Label(root, text="■ 後でやりたいこと、メモなど", font=("Helvetica", 10, "bold"))
label_memo.pack(pady=(10, 0))
entry_memo = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
entry_memo.pack(pady=PAD_Y)

send_button = tk.Button(root, text="Notionに送信", command=send_to_notion, 
                        width=20, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_button.pack(pady=20)

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
output_box.pack(pady=5)

root.mainloop()