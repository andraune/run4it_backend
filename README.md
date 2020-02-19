# run4it_backend

[![CircleCI](https://circleci.com/gh/andraune/run4it_backend.svg?style=svg)](https://circleci.com/gh/andraune/run4it_backend)

Quickstart - Development
---
Start by creating a file '.flaskenv' with the following contents:

	FLASK_APP=run4it_backend.py
	FLASK_DEBUG=1
	FLASK_ENV=development

Install required packages:

	- Create and activate virtual python environment
	- Make project root folder your working directory
	- pip install -r requirements/dev.txt

Define environment variables in a file called .flaskenv (not included in git repo):

	FLASK_APP=run4it_backend.py
	FLASK_DEBUG=1
	FLASK_ENV=development

In order to create database tables and create inital migration:

	flask db init
	flask db migrate
	flask db upgrade

When making database changes, create migration scripts and upgrade using 'migrate' and 'upgrade'. Only 'upgrade' must be used after pulling new migration scripts.

Repeat the last two commands to update database when models have been added or modified. To run the web application, use:

	flask run

Run unit tests:

	flask tests

Other useful commands defined in app:

	flask clean
	flask init-test-data	// init_test_data in some Python versions
	flask shell
	init_and_test.bat		// run tests with newman, Windows
	./init_and_test.sh		// run tests with newman, Linux

Production (assuming Linux)
---
Define environment variables ('export' or define in .profile or equivalent):

	FLASK_APP=/path/to/run4it_backend.py
	FLASK_DEBUG=0
	RUN4IT_SECRET_KEY=<something-really-secret>
	RUN4IT_JWT_SECRET_KEY=<something-equally-secret>
	RUN4IT_DB_URL=<postgre database URL>
