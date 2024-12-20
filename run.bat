@echo off
title USB無くした
cd /d %~dp0

start python index.py

cd stable-diffusion-webui-forge
webui.bat --nowebui