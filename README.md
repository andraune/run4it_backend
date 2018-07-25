# run4it_backend

flask db init

flask db migrate

flask db upgrade

flask run


launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask",
            "type": "python",
            "request": "launch",
            "stopOnEntry": false,
            "pythonPath": "${config:python.pythonPath}",
            "module": "flask.cli",
            "cwd": "${workspaceRoot}",
      
            "env": {
                "FLASK_APP": "run4it_backend.py",
                "FLASK_DEBUG": 1,
                "LC_ALL": "en_US.utf-8",
                "LANG": "en_US.utf-8"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload",
                "--with-threads"
            ],
            "debugOptions": [
                "WaitOnAbnormalExit",
                "WaitOnNormalExit",
                "RedirectOutput"
            ]
        }
    ]
}
