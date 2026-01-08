@echo off
set GIT_PATH="C:\Users\X1C\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"

echo [CHECK] Checking for Git at found path...
if not exist %GIT_PATH% (
    echo [ERROR] Git not found at %GIT_PATH%
    echo Please check if GitHub Desktop is installed correctly.
    pause
    exit /b
)

echo [GIT] Adding files to staging area...
%GIT_PATH% add .

echo [GIT] Committing changes...
%GIT_PATH% commit -m "Update project: Add .gitignore and AIProject files"

echo [GIT] Pushing to branch )))) ...
%GIT_PATH% push origin ))))

echo [DONE] Operations completed.
pause
