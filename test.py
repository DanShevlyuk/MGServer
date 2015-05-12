from app.models import *
from app import db

questions = Question.query.all()
movies = Movie.query.all()

aq = QuestionWithStat()
print "id: " + str(aq.id)

aq.movie = movies[0]
aq.question = questions[0]

db.session.add(aq)
db.session.commit()

print "id: " + str(aq.id)

qws = QuestionWithStat.query.all()
print qws

print u"%s" % movies[0].questions_stat
