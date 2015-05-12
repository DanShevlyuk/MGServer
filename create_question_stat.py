from app.models import *
from app import db
from app.utils import init_stat
from app.utils.parsers import *

db.drop_all()
db.create_all()
questions_parse("test_questions.txt")
movies_parse("test_movies.txt")

movies = Movie.query.all()
questions = Question.query.all()

for m in init_stat.keys():
    for q in init_stat[m].keys():
        qStat = QuestionWithStat()
        qStat.movie = Movie.query.filter_by(name=m).all()[0]
        qStat.question = Question.query.filter_by(text=q).all()[0]
        qStat.yes_answers = int(init_stat[m][q]['yes'])
        qStat.no_answers = int(init_stat[m][q]['no'])
        qStat.idunno_answers = int(init_stat[m][q]['idunno'])
        db.session.add(qStat)
        db.session.commit()



