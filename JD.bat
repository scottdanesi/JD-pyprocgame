REM This script will launch the Judge Dredd Application

REM Clear out the PYC Files in this directory
DEL *.pyc

REM Launch the JD Game
cd /d C:\P-ROC\pyprocgame
python games/jd/jd.py

REM Pause in case an error occours
pause