from app import manager
from app.utils.parsers import *
from flask.ext.migrate import Migrate, MigrateCommand

@manager.command
def init():
    db.drop_all()
    db.create_all()
    questions_parse('questions.txt')
    movies_parse('movies.txt')

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

