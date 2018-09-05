"""Click commands"""
import click, os
from flask.cli import with_appcontext


@click.command()
@with_appcontext
def initdata():
    """Command used to delete database data. Intended for testing.
    Should maybe try to guard this against use in production."""
    ret_code = init_database_data()
    exit(ret_code)


@click.command()
@with_appcontext
def clean():
    """Remove *.pyc and *.pyo files"""
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)  


@click.command()
def tests():
    """Command used for running tests"""
    import pytest # noqa
    project_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
    test_path = os.path.join(project_root, "tests")
    ret_code = pytest.main([test_path, '--verbose'])
    exit(ret_code)


def init_database_data():
    print('Deleting database data ...')

    from run4it.app.database import db  # noqa
    from run4it.api.user import User  # noqa

    rows = User.query.delete()

    if rows > 0:
        print('Deleted {0} rows from User table'.format(rows))

    user = User('existing', 'existing@user.com', 'pwd')
    user.save()
    print("Added User '{0}'".format(user.username))
    """
    state_names = ['TODO', 'In Progress', 'Review', 'Done']

    for state_name in state_names:
        state = ProgressState(state_name)
        state.save()
        
    """
    print('Application data initialized!')
    return 0


