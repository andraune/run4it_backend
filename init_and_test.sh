#!/bin/bash
source flaskenv/bin/activate
flask init-test-data
deactivate
newman run newman/collection.json -e newman/environment.json
