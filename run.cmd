@echo off
rem 切換工作目錄至批次檔所在目錄
cd /d "%~dp0"
if not defined _OLD_VIRTUAL_PROMPT (
    call env\Scripts\activate
)
rem 啟動 Flask 應用並等待幾秒鐘讓它啟動
start "" /B cmd /C "flask --debug -A app run -h 0.0.0.0 -p 80"
start "" "http://192.168.1.102"
