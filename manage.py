from app import manager, db
from app.utils.parsers import *

@manager.command
def init():
    db.drop_all()
    db.create_all()
    questions_parse('questions.txt')
    movies_parse('movies_list.csv')

if __name__ == '__main__':
    manager.run()


