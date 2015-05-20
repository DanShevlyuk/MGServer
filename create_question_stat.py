from app.models import *
from app import db
from app.utils import init_stat
from app.utils.parsers import *

db.drop_all()
db.create_all()
questions_parse("questions.txt")
movies_parse("movies.txt")

movies = Movie.query.all()
questions = Question.query.all()

for m_id, stat in init_stat.iteritems():
    qStat = QuestionWithStat()
    qStat.movie_id = m_id
    qStat.question_id = stat['question_id']
    qStat.yes_answers = stat['yes_answers']
    qStat.no_answers = stat['no_answers']
    qStat.idunno_answers = stat['idunno_answers']


