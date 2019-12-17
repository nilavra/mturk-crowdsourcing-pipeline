@echo off
rem
rem create custom qualification
rem 
rem 

call _getVars.cmd


cd /d %MTURK_CMD_HOME%\bin

call assignQualification -donotnotify -input %MTURK_PROJ_PATH%\%MTURK_QUAL_NAME%.properties.success -scorefile %MTURK_PROJ_PATH%\%MTURK_WORKER_LIST%

cd /d %MTURK_PROJ_PATH%

