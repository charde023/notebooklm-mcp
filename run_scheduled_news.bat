@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "C:\workspace\Daily_news\notebooklm-mcp"
if not exist logs mkdir logs
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set logdate=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%
echo ================================================== >> "logs\daily_news_%logdate%.log"
echo [ %datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2% ] 스케줄 작업 시작 >> "logs\daily_news_%logdate%.log"
"C:\Users\inwon\.local\bin\uv.exe" run "C:\workspace\Daily_news\notebooklm-mcp\run_all_news.py" >> "logs\daily_news_%logdate%.log" 2>&1
