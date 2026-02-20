


# --- 設定（あとでAlexaコンソールの「設定」→「環境変数」に追加してください） ---
# --- 設定 ---
NOTION_TOKEN = ""  # ← あなたのNotionトークン
DATABASE_ID = ""     # ← あなたのデータベースID
GEMINI_KEY = ""    # ← あなたのGemini APIキー


import logging
import ask_sdk_core.utils as ask_utils
import os
import requests
import json
from datetime import datetime, timezone, timedelta

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==========================================
# 【重要】ここにAPIキーを入力してください！
# ==========================================

# ==========================================

class LaunchRequestHandler(AbstractRequestHandler):
    """スキルが起動された時の処理"""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "「メモして」といって"
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class JournalIntentHandler(AbstractRequestHandler):
    """メインの記録処理"""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("JournalIntent")(handler_input)

    def handle(self, handler_input):
        raw_text = ask_utils.get_slot_value(handler_input, "rawText")
        
        try:
            parsed_data = self.analyze_with_gemini(raw_text)
            self.send_to_notion(parsed_data)
            
            done_text = parsed_data.get('done', '')
            if done_text:
                speak_output = f"記録しました。{done_text}、ですね。お疲れ様です。"
            else:
                speak_output = "ジャーナルに記録しました。"
                
        except Exception as e:
            logger.error(e)
            # エラーの詳細をアレクサに喋らせるデバッグモード
            speak_output = f"すみません、エラーが発生しました。詳細は、{str(e)} です。"

        return handler_input.response_builder.speak(speak_output).response

    def analyze_with_gemini(self, text):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_KEY}"
        prompt = f"""
        以下のテキストは、作業中のユーザーが書いたジャーナルメモです。
        文脈を読み取り、以下の4つの要素に分類・抽出してJSON形式で出力してください。
        該当する内容がない要素は空文字("")にしてください。

        【分類する項目】
        - "done": 完了したこと（簡潔なタイトルとして抽出）
        - "next": 次にやりたいこと
        - "mood": 感情・状況
        - "memo": 後でやりたいこと、その他のメモなど

        【入力テキスト】
        {text}
        """
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "responseMimeType": "application/json"}
        }
        res = requests.post(url, json=payload)
        res.raise_for_status()
        
        # Python 3.8対応のマークダウン除去（replaceを使用）
        response_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_text)
    
    def send_to_notion(self, data):
        JST = timezone(timedelta(hours=+9), 'JST')
        current_time = datetime.now(JST).isoformat()
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        done_text = data.get("done", "")
        next_text = data.get("next", "")
        mood_text = data.get("mood", "")
        memo_text = data.get("memo", "")
        
        if not done_text:
            done_text = " "
            
        properties = {
            "title": {"title": [{"text": {"content": done_text}}]},
            "I%5BJp": {"date": {"start": current_time}},
            "udPY": {"rich_text": [{"text": {"content": next_text}}] if next_text else []},
            "cNJ%5C": {"rich_text": [{"text": {"content": mood_text}}] if mood_text else []},
            "c%3BQ%7C": {"rich_text": [{"text": {"content": memo_text}}] if memo_text else []}
        }
        
        body = {
            "parent": {"database_id": DATABASE_ID},
            "properties": properties
        }
        
        res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=body)
        if res.status_code != 200:
            logger.error(f"Notion API Error: {res.text}") 
        res.raise_for_status()

# --- その他、終了処理などのハンドラー ---
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak("今の状況を話すとNotionに記録します。").response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
    def handle(self, handler_input):
        return handler_input.response_builder.speak("さようなら").response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)
    def handle(self, handler_input):
        speak_output = "すみません、うまく認識できませんでした。もう一度「メモして、〇〇」のように言ってみてください。"
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        return handler_input.response_builder.speak("予期せぬエラーが発生しました。").response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(JournalIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler()) 
sb.add_exception_handler(CatchAllExceptionHandler())
lambda_handler = sb.lambda_handler()