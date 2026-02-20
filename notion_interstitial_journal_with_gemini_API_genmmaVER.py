import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import re  # 正規表現を使ってJSONを抽出するために追加
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os
import google.generativeai as genai

# .envファイルを読み込み
load_dotenv()

# --- 設定 ---
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini APIの設定
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("警告: GEMINI_API_KEYが設定されていません。")

# Geminiモデルのセットアップ (JSONで出力するように設定)
generation_config = {
    "temperature": 0.4, # 事実ベースで抽出させるため、少し低めに設定
    "top_p": 0.95,
    # "top_k": 64,
    # "max_output_tokens": 8192,
    # "response_mime_type": "application/json", # JSON形式の出力を強制 (Gemmaでは使用不可のためコメントアウト)
}
model = genai.GenerativeModel(
    model_name="gemma-3-27b-it",
    generation_config=generation_config,
)

# Notion用ヘッダー
notion_headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def log_message(msg):
    """ログ出力用のヘルパー関数"""
    JST = timezone(timedelta(hours=+9), 'JST')
    log_time = datetime.now(JST).strftime('%H:%M:%S')
    output_box.insert(tk.END, f"[{log_time}] {msg}\n")
    output_box.see(tk.END)
    root.update()

def process_and_send():
    raw_text = entry_main.get("1.0", tk.END).strip()
    
    if not raw_text:
        log_message("エラー: テキストが入力されていません。")
        return

    log_message("Geminiでテキストを解析中...")
    send_button.config(state=tk.DISABLED) # 二重送信防止

    try:
        # 1. Geminiに投げるプロンプトの作成
        prompt = f"""
                以下のテキストは、作業中のユーザーが書いたジャーナルメモです。
                文脈を読み取り、以下の4つの要素に分類・抽出してJSON形式で出力してください。
                該当する内容がない要素は空文字("")にしてください。
                
                ユーザーの入力した文章を勝手に書き換えないでください。
                入力された生の言葉を、そのままの長さで各項目に振り分けてください。
                「えー」「あー」「んーと」などのフィラー（意味のない繋ぎ言葉）は、内容を損なわない範囲で削除してください。
                誤字脱字の修正は行ってください。
                文章の区切りがわかりにくい場合は、改行や、【。】【、】句読点などをくわえてください。

                【分類する項目】
                - "done": 完了したこと（簡潔なタイトルとして抽出）
                - "next": 次にやりたいこと
                - "mood": 感情・状況
                - "memo": 後でやりたいこと、その他のメモなど

                【重要】
                以下のテキストを解析し、必ず指定したJSONフォーマットのみで出力してください。
                マークダウンのコードブロック（```json ... ```）は使用せず、生のJSONテキストのみを出力してください。

                【出力フォーマット】
                {{
                    "done": "完了したタスクのタイトル",
                    "next": "次にやること",
                    "mood": "今の気分や状況",
                    "memo": "その他のメモ"
                }}

                【入力テキスト】
                {raw_text}
                """

        # 2. Gemini APIの呼び出し
        response = model.generate_content(prompt)
        response_text = response.text
        
        # ==========================================
        # デバッグ用：AIの生の返答をコンソールに表示
        # ==========================================
        print("\n" + "="*50)
        print("【デバッグ】AIからの生の返答:")
        print(response_text)
        print("="*50 + "\n")
        # ==========================================

        # 正規表現で {...} の部分（JSON文字列）だけを抽出する
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            parsed_data = json.loads(json_str)
        else:
            log_message("エラー: AIの返答からJSONを見つけられませんでした。")
            log_message(f"AIの実際の返答:\n{response_text}")
            send_button.config(state=tk.NORMAL)
            return

        # 抽出したデータの取得
        done_text = parsed_data.get("done", "")
        next_text = parsed_data.get("next", "")
        mood_text = parsed_data.get("mood", "")
        memo_text = parsed_data.get("memo", "")

        # 抽出結果をログに表示（確認用）
        log_message(f"[抽出完了] Done: {done_text[:10]}... Next: {next_text[:10]}...")

        # 3. 現在の日時を日本時間(JST)で取得
        JST = timezone(timedelta(hours=+9), 'JST')
        current_time = datetime.now(JST).isoformat()

        # 4. Notionに送信するデータの構築
        notion_data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "title": {"title": [{"text": {"content": done_text}}]},
                "I%5BJp": {"date": {"start": current_time}},
                "udPY": {"rich_text": [{"text": {"content": next_text}}]},
                "cNJ%5C": {"rich_text": [{"text": {"content": mood_text}}]},
                "c%3BQ%7C": {"rich_text": [{"text": {"content": memo_text}}]}
            }
        }

        # 5. Notion APIへのリクエスト送信
        log_message("Notionへデータを送信中...")
        notion_response = requests.post(NOTION_API_URL, headers=notion_headers, data=json.dumps(notion_data))

        if notion_response.status_code == 200:
            log_message("✨ Notionへの送信が成功しました！")
            entry_main.delete("1.0", tk.END) # 入力欄をクリア
        else:
            log_message(f"Notionエラー: {notion_response.status_code}")
            log_message(f"{notion_response.json()}")

    except json.JSONDecodeError:
        log_message("エラー: 抽出したテキストをJSONとして解析できませんでした。")
    except Exception as e:
        log_message(f"エラーが発生しました: {e}")
    finally:
        # ボタンを再度有効化
        send_button.config(state=tk.NORMAL)


# ==========================================
# GUIアプリケーションの作成
# ==========================================
root = tk.Tk()
root.title("AIインタースティシャル・ジャーナリング")
root.geometry("500x650")

PAD_Y = 10

# メイン入力欄
label_main = tk.Label(root, text="■ 今の状況や考えていることを書き出してください", font=("Helvetica", 10, "bold"))
label_main.pack(pady=(20, 5))

entry_main = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=55, height=15)
entry_main.pack(pady=PAD_Y)

# 送信ボタン
send_button = tk.Button(root, text="AIで振り分けてNotionに送信", command=process_and_send, 
                        width=30, height=2, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
send_button.pack(pady=20)

# 出力ログ
output_label = tk.Label(root, text="実行ログ:")
output_label.pack(pady=(5, 0))
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=55, height=8)
output_box.pack(pady=5)

root.mainloop()