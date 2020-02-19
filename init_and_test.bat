@echo off
flask init-test-data
newman run newman/collection.json -e newman/environment.json
