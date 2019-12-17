@echo off
rem
rem create custom qualification
rem 
rem 

call _getVars.cmd


cd /d %MTURK_CMD_HOME%\bin

call blockWorker -workerid <<worker_id>> -reason "Reason."

call unblockWorker -workerid <<worker_id>> -reason "Reason."

cd /d %MTURK_PROJ_PATH%

