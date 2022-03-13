@echo off
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
::   QUICK TEST FOR UNDETECTED-CHROMEDRIVER TO CHECK IF CLOUDFLARE IAUAM CAN BE PASSED
::   
::   To make it as clean as possible without interfering packages or plugins:
::     - this creates a new python virtual environment
::     - installs undetected chromedriver
::     - executes a test
::     - cleans up the virtual environment
::
::   this is for Windows only currently
::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


set uc_test_dir=%temp%\ucvenv

set curdir=%CD%
set prog=


:: ===================
:main

call :hasprog "conda"
if [%prog%]==[conda]  (
    echo "conda is found, activating..."
    call %prog% activate
    goto :next
    exit
)

call :hasprog "python"
if [%prog%]==[python] (
    echo "python is found"
    goto :next
    exit
)

echo "no python interpreter or conda could be found. exiting"
exit 1



:: ===================
:hasprog
call %~1 --help  >nul 2>&1
if ERRORLEVEL 0 (
    set prog=%~1
)
exit /B



:: ===================
:next

mkdir %uc_test_dir%
echo "created temp directory for the virtual environment: %uc_test_dir%"

python -m venv %uc_test_dir%

set pythonv=%uc_test_dir%\scripts\python
%pythonv% -m pip install -U undetected-chromedriver
%pythonv% -c  "exec(\"import time,logging,undetected_chromedriver as uc,selenium.webdriver.support.expected_conditions as ec,selenium.webdriver.support.wait as wwait;logging.basicConfig(level=10);dr=uc.Chrome();dr.get('https://nowsecure.nl');wwait.WebDriverWait(dr,15).until(ec.visibility_of_element_located(('css selector','.hystericalbg')));print('====================WORKING=============');time.sleep(3)\")"
                

if [%prog%]==[conda] ( 
    echo "deactivating conda env"
    %prog% deactivate
)

cd %curdir%
rd /S /Q %uc_test_dir%
echo "cleaning up temp directory for the virtual environment: %uc_test_dir%"




