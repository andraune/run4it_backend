@echo off
cd \idev\run4it_backend
call start cmd /k "flaskenv\scripts\activate.bat"
call flaskenv\scripts\activate.bat
cmd /k "flask run"
