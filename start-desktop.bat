@echo off
cd /d "%~dp0frontend"
start /min npm run electron:dev
