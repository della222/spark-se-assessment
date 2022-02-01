import os
import sys
import dotenv

dotenv.load_dotenv()

if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(
        branch=True,
        include='project/*',
        omit=[
            'project/tests/*',
            'project/server/config.py',
            'project/server/*/__init__.py'
        ]
    )
    COV.start()

import click
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
if os.getenv("ENV") == "PROD":
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://tpocynlbojyyds:f95d0ea19807a96b0f4fbf1389d610414179b357d8e15d976ca58553d7cc77ed@ec2-52-20-143-167.compute-1.amazonaws.com:5432/d94rm99kbf4p0j"

from project.server.models import User
migrate = Migrate(app, db)


@app.route("/")
def root_site():
    return "<p>It works!</p>"

from project.server.auth.views import auth_blueprint
from project.server.users.views import users_blueprint
app.register_blueprint(auth_blueprint)
app.register_blueprint(users_blueprint)

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
                help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        if COV:
            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()
            basedir = os.path.abspath(os.path.dirname(__file__))
            covdir = os.path.join(basedir, 'tmp/coverage')
            COV.html_report(directory=covdir)
            print('HTML version: file://%s/index.html' % covdir)
            COV.erase()
        return 0
    return 1
