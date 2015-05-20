from app import manager
from app.utils.parsers import *

@manager.command
def init():
    db.drop_all()
    db.create_all()
    questions_parse('questions.txt')
    movies_parse('movies.txt')

if __name__ == '__main__':
    manager.run()


