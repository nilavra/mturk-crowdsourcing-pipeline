@echo off
rem
rem create custom qualification
rem 
rem 

call _getVars.cmd

rem if .success file exists, abort
if exist %MTURK_PROJ_PATH%\%MTURK_QUAL_NAME%.properties.success (
    REM abort
    echo  ERROR: 
    echo         %MTURK_QUAL_NAME%.properties.success file already exists!! 
    echo  Aborting
    exit /b
) 

REM Proceed normally
cd /d %MTURK_CMD_HOME%\bin

call createQualificationType -properties %MTURK_PROJ_PATH%\%MTURK_QUAL_NAME%.properties  -noretry

cd /d %MTURK_PROJ_PATH%




