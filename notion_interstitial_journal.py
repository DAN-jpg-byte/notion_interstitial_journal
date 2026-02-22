

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

# ヘッダーの設定
headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Notionにデータを送信する関数
def send_to_notion():
    # 1. 各入力欄からテキストを取得
    # strip() で前後の余計な改行や空白を削除
    done_text = entry_done.get("1.0", tk.END).strip()      # 完了したこと（タイトル）
    next_text = entry_next.get("1.0", tk.END).strip()      # 次にやりたいこと
    mood_text = entry_mood.get("1.0", tk.END).strip()      # 気持ち
    memo_text = entry_memo.get("1.0", tk.END).strip()      # 後でやりたいこと、メモなど

    # 【修正ポイント】必須チェックを外し、空なら空文字にする処理
    # (strip()しているので、未入力なら自動的に "" になります)

    # 2. 現在の日時を日本時間(JST)で取得
    JST = timezone(timedelta(hours=+9), 'JST')
    current_time = datetime.now(JST).isoformat()

# 3. Notionに送信するデータの構築
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            # 「完了したこと」のID: title
            "title": {
                "title": [
                    {
                        "text": {"content": done_text}
                    }
                ]
            },
            # 「日時」のID: I%5BJp
            "I%5BJp": {
                "date": {
                    "start": current_time
                }
            },
            # 「次にやりたいこと」のID: udPY
            "udPY": {
                "rich_text": [{"text": {"content": next_text}}]
            },
            # 「気持ち」のID: cNJ%5C
            "cNJ%5C": {
                "rich_text": [{"text": {"content": mood_text}}]
            },
            # 「後でやりたいこと、メモなど」のID: c%3BQ%7C
            "c%3BQ%7C": {
                "rich_text": [{"text": {"content": memo_text}}]
            }
        }
    }

    # 4. Notion APIへのリクエスト送信
    try:
        response = requests.post(NOTION_API_URL, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            # 成功時のログ（JST）
            log_time = datetime.now(JST).strftime('%H:%M:%S')
            output_box.insert(tk.END, f"[{log_time}] 送信成功！\n")
            
            # 入力欄をクリア
            entry_done.delete("1.0", tk.END)
            entry_next.delete("1.0", tk.END)
            entry_mood.delete("1.0", tk.END)
            entry_memo.delete("1.0", tk.END)
            # スクロールを一番下へ
            output_box.see(tk.END)
        else:
            output_box.insert(tk.END, f"エラー: {response.status_code}\n")
            output_box.insert(tk.END, f"{response.json()}\n")
            output_box.see(tk.END)
            
    except Exception as e:
        output_box.insert(tk.END, f"通信エラーが発生しました: {e}\n")
        output_box.see(tk.END)

# ==========================================
# GUIアプリケーションの作成
# ==========================================
root = tk.Tk()
root.title("インタースティシャル・ジャーナリング")
root.geometry("500x750")

PAD_Y = 5

# --- 各入力欄の配置（既存通り） ---
label_done = tk.Label(root, text="■ 完了したこと (Title)", font=("Helvetica", 10, "bold"))
label_done.pack(pady=(10, 0))
entry_done = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_done.pack(pady=PAD_Y)

label_next = tk.Label(root, text="■ 次にやりたいこと・目的", font=("Helvetica", 10, "bold"))
label_next.pack(pady=(10, 0))
entry_next = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=3)
entry_next.pack(pady=PAD_Y)

label_mood = tk.Label(root, text="■ 気持ち", font=("Helvetica", 10, "bold"))
label_mood.pack(pady=(10, 0))
entry_mood = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=2)
entry_mood.pack(pady=PAD_Y)

label_memo = tk.Label(root, text="■ 後でやりたいこと、メモなど", font=("Helvetica", 10, "bold"))
label_memo.pack(pady=(10, 0))
entry_memo = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
entry_memo.pack(pady=PAD_Y)

# 送信ボタン
send_button = tk.Button(root, text="Notionに送信", command=send_to_notion, 
                        width=20, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_button.pack(pady=20)

# 出力ログ
output_label = tk.Label(root, text="ログ:")
output_label.pack(pady=(5, 0))
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=4)
output_box.pack(pady=5)

root.mainloop()