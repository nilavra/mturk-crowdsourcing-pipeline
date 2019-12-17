@echo off
rem
rem create custom qualification
rem 
rem 

call _getVars.cmd


cd /d %MTURK_CMD_HOME%\bin

call rejectWork -rejectfile %MTURK_PROJ_PATH%\%MTURK_REJECT_LIST%

cd /d %MTURK_PROJ_PATH%

