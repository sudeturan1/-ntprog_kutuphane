@echo off
cd /d %~dp0
echo Sunucu başlatılıyor...
set FLASK_APP=run.py
set FLASK_DEBUG=1
python -m flask run
pause
