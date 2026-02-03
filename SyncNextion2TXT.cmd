@echo off
python dev\Nextion2Text.py -i hmi\nspanel_eu.HMI -o hmi\dev\nspanel_eu_code -p visual unknown
if errorlevel 1 timeout /t 10
python dev\Nextion2Text.py -i hmi\nspanel_us.HMI -o hmi\dev\nspanel_us_code -p visual unknown
if errorlevel 1 timeout /t 10
python dev\Nextion2Text.py -i hmi\nspanel_us_land.HMI -o hmi\dev\nspanel_us_land_code -p visual unknown
if errorlevel 1 timeout /t 10
python dev\Nextion2Text.py -i hmi\nspanel_CJK_eu.HMI -o hmi\dev\nspanel_CJK_eu_code -p visual unknown
if errorlevel 1 timeout /t 10
python dev\Nextion2Text.py -i hmi\nspanel_CJK_us.HMI -o hmi\dev\nspanel_CJK_us_code -p visual unknown
if errorlevel 1 timeout /t 10
python dev\Nextion2Text.py -i hmi\nspanel_CJK_us_land.HMI -o hmi\dev\nspanel_CJK_us_land_code -p visual unknown
if errorlevel 1 timeout /t 10
xcopy /y /d hmi\*.tft H:\www\nspanel\dev
if errorlevel 1 timeout /t 10
 
timeout /t 30
