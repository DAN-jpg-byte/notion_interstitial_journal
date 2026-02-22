Set ws = CreateObject("WScript.Shell")
' 実行するコマンド（Pythonスクリプトのフルパスを指定）
command = "pythonw ""C:\Users\user\Desktop\PROGRAM DEVELOPMENT\python\Notion-programs\notion_interstitial_journal\notion_interstitial_journal.py"""
' 0 はウィンドウを非表示にする設定です
ws.Run command, 0, False