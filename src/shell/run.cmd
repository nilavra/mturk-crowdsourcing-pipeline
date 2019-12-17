@echo off
rem
rem Copyright 2012 Amazon Technologies, Inc.
rem 
rem Licensed under the Amazon Software License (the "License");
rem you may not use this file except in compliance with the License.
rem You may obtain a copy of the License at:
rem 
rem http://aws.amazon.com/asl
rem 
rem This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
rem OR CONDITIONS OF ANY KIND, either express or implied. See the
rem License for the specific language governing permissions and
rem limitations under the License.
rem 
rem 

call _getVars.cmd

rem if .success file exists, abort
if exist %MTURK_PROJ_PATH%\%MTURK_LBL%_%MTURK_MODE%.success (
    REM abort
    echo  ERROR: 
    echo         %MTURK_LBL%_%MTURK_MODE%.success file already exists!! 
    echo  Aborting
    exit /b
) 

REM Proceed normally
cd /d %MTURK_CMD_HOME%\bin

call loadHITs %1 %2 %3 %4 %5 %6 %7 %8 %9 -label %MTURK_PROJ_PATH%\%MTURK_LBL%_%MTURK_MODE% -input %MTURK_PROJ_PATH%\%MTURK_LBL%.input -question %MTURK_PROJ_PATH%\%MTURK_QSN% -properties %MTURK_PROJ_PATH%\%MTURK_PRP%

cd /d %MTURK_PROJ_PATH%




