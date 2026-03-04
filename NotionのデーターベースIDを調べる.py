

import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv
import os
# .envファイルを読み込み
load_dotenv()


# --- 設定 ---

NOTION_API_TOKEN  = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1/pages"

def get_notion_db_ids():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN }",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 1件だけ取得するためのデータ
    data = json.dumps({"page_size": 1}).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as res:
            body = json.loads(res.read().decode("utf-8"))
            results = body.get("results")
            
            if not results:
                print("データベースが空です。1件入力してから実行してください。")
                return

            properties = results[0].get("properties")
            
            print("--- データベースの列情報 (ID確定版) ---")
            for prop_name, prop_data in properties.items():
                p_id = prop_data.get("id")
                p_type = prop_data.get("type")
                print(f"列名: {prop_name}")
                print(f"  ID  : {p_id}")
                print(f"  型  : {p_type}")
                print("-" * 30)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    get_notion_db_ids()