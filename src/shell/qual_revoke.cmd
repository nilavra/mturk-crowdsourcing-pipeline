@echo off
rem
rem create custom qualification
rem 
rem 

call _getVars.cmd


cd /d %MTURK_CMD_HOME%\bin

call revokeQualification -qualtypeid 3IUAW6PFBFUXX9NZN2Y02B3301Z6QN -workerid <<worker_id>>

cd /d %MTURK_PROJ_PATH%

