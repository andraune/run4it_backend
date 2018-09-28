@echo off
flask init_test_data
newman run newman/collection.json -e newman/environment.json
