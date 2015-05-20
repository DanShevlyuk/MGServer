# -*- coding: utf-8 -*-
# dict = {}

from app.utils.parsers import *
from app import db
from random import randint
from app.models import *

db.drop_all()
db.create_all()
questions_parse("questions.txt")
movies_parse("movies.txt")

movies = Movie.query.all()
questions = Question.query.all()

for movie in movies:
    for question in questions:
        ans = raw_input(u"[%s] %s : " % (movie.name, question.text))
        if ans == 's':
            continue

        qStat = QuestionWithStat()
        qStat.movie = movie
        qStat.question = question

        if ans == "y":
            qStat.yes_answers = randint(15, 20)
            qStat.no_answers = randint(0, 3)
            qStat.idunno_answers = randint(0, 5)
            db.session.add(qStat)
            db.session.commit()

        elif ans == "n":
            qStat.yes_answers = randint(0, 3)
            qStat.no_answers = randint(15, 20)
            qStat.idunno_answers = randint(0, 5)
            db.session.add(qStat)
            db.session.commit()
        elif ans == "i":
            qStat.yes_answers = randint(0, 3)
            qStat.no_answers = randint(0, 3)
            qStat.idunno_answers = randint(7, 12)
            db.session.add(qStat)
            db.session.commit()
        else:
            continue


# string_dict = str(dict)

# print string_dict
#
# with open('string_dict.txt', 'w') as fp:
#     fp.write(string_dict)
#





