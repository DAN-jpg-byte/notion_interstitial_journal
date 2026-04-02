import tkinter as tk
from tkinter import scrolledtext
import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

# .envファイルを読み込み
load_dotenv()

# --- 設定 ---
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("PLAN_DATABASE_ID")

NOTION_API_URL = "https://api.notion.com/v1/pages"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def send_to_notion():
    # 1. 各入力欄からテキストを取得
    title_text = entry_title.get("1.0", tk.END).strip()   # 名前 (title)
    goal_text = entry_goal.get("1.0", tk.END).strip()     # 目的 (%3DVzQ)
    url_text = entry_url.get("1.0", tk.END).strip()       # URL (%5DrhS)

    if not title_text:
        output_box.insert(tk.END, "エラー: 名前は必須です。\n")
        return

    # 2. 現在の日付を取得 (YYYY-MM-DD 形式)
    JST = timezone(timedelta(hours=+9), 'JST')
    current_date = datetime.now(JST).strftime('%Y-%m-%d')

    # 3. Notion送信データの構築
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            # 名前 (Title)
            "title": {"title": [{"text": {"content": title_text}}]},
            
            # 目的 (rich_text) - ID: %3DVzQ
            "%3DVzQ": {
                "rich_text": [{"text": {"content": goal_text}}]
            },
            
            # URL - ID: %5DrhS
            "%5DrhS": {
                "url": url_text if url_text else None
            },
            
            # いつやるか？ (date) - ID: RV%40e (日付のみ)
            "RV%40e": {
                "date": {"start": current_date}
            }
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            log_time = datetime.now(JST).strftime('%H:%M:%S')
            output_box.insert(tk.END, f"[{log_time}] 送信成功！\n")
            
            # 入力欄をクリア
            entry_title.delete("1.0", tk.END)
            entry_goal.delete("1.0", tk.END)
            entry_url.delete("1.0", tk.END)
            output_box.see(tk.END)
        else:
            output_box.insert(tk.END, f"エラー: {response.status_code}\n")
            output_box.see(tk.END)
    except Exception as e:
        output_box.insert(tk.END, f"通信エラー: {e}\n")

# --- GUI ---
root = tk.Tk()
root.title("Notion Quick Add")
root.geometry("500x550")

PAD_Y = 5




label_title = tk.Label(root, text="PLAN・タスク入力用", font=("Helvetica", 30, "bold"))
label_title.pack(pady=(10, 0))

# ■ 名前
label_title = tk.Label(root, text="■ PLAN・タスク名", font=("Helvetica", 10, "bold"))
label_title.pack(pady=(10, 0))
entry_title = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_title.pack(pady=PAD_Y)

# ■ 目的
label_goal = tk.Label(root, text="■ 目的", font=("Helvetica", 10, "bold"), fg="#2E7D32")
label_goal.pack(pady=(10, 0))
entry_goal = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_goal.pack(pady=PAD_Y)

# ■ URL
label_url = tk.Label(root, text="■ 関連URL", font=("Helvetica", 10, "bold"), fg="#1976D2")
label_url.pack(pady=(10, 0))
entry_url = tk.Text(root, width=50, height=2)
entry_url.pack(pady=PAD_Y)

# 送信ボタン
send_button = tk.Button(root, text="Notionに登録", command=send_to_notion, 
                        width=30, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_button.pack(pady=20)

# ログ出力
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
output_box.pack(pady=5)

root.mainloop()