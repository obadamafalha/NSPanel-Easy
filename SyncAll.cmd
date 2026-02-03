@echo off
xcopy /y /d H:\blueprints\automation\edwardtfn\nspanel_blueprint_dev.yaml .\nspanel_blueprint.yaml
if errorlevel 1 timeout /t 10
xcopy /y /d H:\esphome\packages\edwardtfn\NSPanel-Easy\nspanel_esphome*.yaml .
if errorlevel 1 timeout /t 10
xcopy /y /d H:\esphome\packages\edwardtfn\NSPanel-Easy\esphome\nspanel_esphome_*.yaml esphome\ 
if errorlevel 1 timeout /t 10
xcopy /y /d /e H:\esphome\packages\edwardtfn\NSPanel-Easy\components\. components\.
if errorlevel 1 timeout /t 10
REM xcopy /y /d /e H:\libraries\. libraries\.
REM if errorlevel 1 timeout /t 10
xcopy /y /d H:\esphome\packages\edwardtfn\NSPanel-Easy\prebuilt\*.yaml prebuilt\ 
if errorlevel 1 timeout /t 10
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
python dev\Nextion2Text.py -i hmi\nspanel_blank.HMI -o hmi\dev\nspanel_blank_code -p visual unknown
if errorlevel 1 timeout /t 10
xcopy /y /d hmi\*.tft H:\www\nspanel\dev
if errorlevel 1 timeout /t 10
 
timeout /t 30
