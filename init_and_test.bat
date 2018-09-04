@echo off
flask initdata
newman run newman/collection.json -e newman/environment.json
