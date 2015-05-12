dict = {}

from app.utils.parsers import *
from app import db
from random import randint

db.drop_all()
db.create_all()
questions_parse("test_questions.txt")
movies_parse("test_movies.txt")

movies  = Movie.query.all()
questions = Question.query.all()

for movie in movies:
    dict[movie.name] = {}
    for question in questions:
        dict[movie.name][question.text] = {"yes": 0, "no": 0, "idunno": 0}
        ans = raw_input("[%s] %s : " % (movie.name, question.text))
        if ans == "yes":
            dict[movie.name][question.text] = {"yes": randint(10, 20), "no": randint(0, 3), "idunno": randint(0, 5)}
        elif ans == "no":
            dict[movie.name][question.text] = {"yes": randint(0, 3), "no": randint(10, 20), "idunno": randint(0, 5)}
        elif ans == "idunno":
            dict[movie.name][question.text] = {"yes": randint(0, 5), "no": randint(0, 5), "idunno": randint(6, 9)}
        else:
            dict[movie.name][question.text] = {"yes": randint(0, 5), "no": randint(0, 5), "idunno": randint(6, 9)}


string_dict = str(dict)

print string_dict




