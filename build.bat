@echo off
pip install -r requirements.txt
pyinstaller --onefile --windowed --name SeaBattle main.py
echo.
echo Done: dist\SeaBattle.exe
pause
