# -*- coding: utf-8 -*-
# dict = {}

from app.utils.parsers import *
from app import db
from random import randint

db.drop_all()
db.create_all()
questions_parse("questions.txt")
movies_parse("movies_list.csv")

movies  = Movie.query.all()
questions = Question.query.all()

for movie in movies:
    dict[movie.name] = {}
    for question in questions:
        ans = raw_input(u"[%s] %s : " % (unicode(movie.name), unicode(question.text)))
        if ans == 'skip':
            continue

        dict[movie.name][question.text] = {"yes": 0, "no": 0, "idunno": 0}

        if ans == "yes":
            dict[movie.name][question.text] = {"yes": randint(15, 20), "no": randint(0, 3), "idunno": randint(0, 5)}
        elif ans == "no":
            dict[movie.name][question.text] = {"yes": randint(0, 3), "no": randint(15, 20), "idunno": randint(0, 5)}
        elif ans == "idunno":
            dict[movie.name][question.text] = {"yes": randint(0, 3), "no": randint(0, 3), "idunno": randint(8, 12)}
        else:
            dict[movie.name][question.text] = {"yes": randint(0, 5), "no": randint(0, 5), "idunno": randint(6, 9)}


string_dict = str(dict)

print string_dict

with open('string_dict.txt', 'w') as fp:
    fp.write(string_dict)






