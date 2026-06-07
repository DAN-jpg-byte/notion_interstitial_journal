Set ws = CreateObject("WScript.Shell")
' notion_add_plan.py (full path). pythonw = no console window.
command = "pythonw ""C:\Users\user\Desktop\PROGRAM DEVELOPMENT\python\Notion-programs\notion_interstitial_journal\notion_add_plan.py"""
' 0 = hidden window style
ws.Run command, 0, False
