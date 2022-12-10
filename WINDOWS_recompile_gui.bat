echo "This requires Python to be installed"
call pip install -r requirements.txt
call pyinstaller --onefile --windowed gui.py
echo "GUI is in dist\gui.exe"
pause