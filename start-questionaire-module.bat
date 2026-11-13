@echo off
cd /d "%~dp0"
docker compose up -d
docker compose ps
start http://localhost:8080