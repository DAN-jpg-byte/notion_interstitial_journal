@echo off
set SCRIPT_PATH="C:\Users\user\Desktop\PROGRAM DEVELOPMENT\python\Notion-programs\notion_interstitial_journal\notion_interstitial_journal.py"

echo Running Notion Interstitial Journal...
:: Ç±Ç±Ç python Ç©ÇÁ pythonw Ç…ïœçX
start /b pythonw %SCRIPT_PATH%

if %errorlevel% neq 0 (
    echo [ERROR] é¿çsÇ…é∏îsÇµÇ‹ÇµÇΩÅB
    pause
)