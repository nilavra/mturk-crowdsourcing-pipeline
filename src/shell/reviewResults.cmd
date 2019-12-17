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
rem -resultsfile [filename]   Specifies the results file that was generated by a call 
rem                           to the getResults command. You must mark the "reject" column 
rem                    of the assignments to reject. All other assignments will be approved.

rem

call _getVars.cmd

cd /d %MTURK_CMD_HOME%\bin

call reviewResults %1 %2 %3 %4 %5 %6 %7 %8 %9 -resultsfile %MTURK_PROJ_PATH%\%MTURK_LBL%_%MTURK_MODE%.results 

cd /d %MTURK_PROJ_PATH%