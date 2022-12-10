#!/bin/sh
echo "This requires Python to be installed"
pip install -r requirements.txt
pyinstaller --onefile --windowed gui.py
echo "GUI is in dist\gui.exe"
read -p "Press Any Key To Exit"