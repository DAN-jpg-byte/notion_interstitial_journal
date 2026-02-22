@echo off
set SCRIPT_PATH="C:\Users\user\Desktop\PROGRAM DEVELOPMENT\python\Notion-programs\notion_interstitial_journal\notion_interstitial_journal.py"

echo Running Notion Interstitial Journal...
python %SCRIPT_PATH%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] スクリプトの実行に失敗しました。
    pause
)