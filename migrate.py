import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object(__name__)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    manager.run()
