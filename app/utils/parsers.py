# from models import questions_stat
from utils import UnicodeReader
from app.models import Movie, Question
from app import db

def questions_parse(file_name):
    with open(file_name, 'rb') as fp:
        reader = UnicodeReader(fp)
        for row in reader:
            text = row[0].strip('"')
            new_question = Question(text=text)
            db.session.add(new_question)
            db.session.commit()

        print "questions added!"

def movies_parse(file_name):
    with open(file_name, 'rb') as fp:
        reader = UnicodeReader(fp)
        for row in reader:
            name = row[0].strip('"')
            # t = row[1].strip('"')
            new_movie = Movie(name=name)
            db.session.add(new_movie)
            db.session.commit()

        print "movies added!"


