# -*- coding: utf-8 -*-

from enum import Enum
from app import db
from utils.math_methods import entropy, bayes, entropy_after_answer
from collections import OrderedDict
import numpy


class Answers(Enum):
    YES = 'yes'
    NO = 'no'
    I_DUNNO = 'I dunno'


class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    times_proposed = db.Column(db.Float)
    questions_stat = db.relationship("QuestionWithStat", backref="movie")

    def __init__(self, name):
        self.name = name
        self.times_proposed = 1.

    def __unicode__(self):
        return u"%s" % (self.name)


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode(64), unique=False, nullable=False)

    def __unicode__(self):
        return u"%s" % (self.text)


class QuestionWithStat(db.Model):
    __tablename__ = "questionwithstat"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    yes_answers = db.Column(db.Integer)
    no_answers = db.Column(db.Integer)
    idunno_answers = db.Column(db.Integer)

    def __init__(self):
        self.yes_answers = 0
        self.no_answers = 0
        self.idunno_answers = 0

    def totalAnswers(self):
        return self.yes_answers + self.no_answers + \
               self.havenoidea_answers + self.doesnotmakesense_answers

    def getAnswersAsDict(self):
        d = {}
        d[Answers.YES] = self.yes_answers
        d[Answers.NO] = self.no_answers
        d[Answers.I_DUNNO] = self.idunno_answers
        return d


class AnswerQuestionPair(object):
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __unicode__(self):
        return u"'%s' >>> %s" % (db.session.query(Question).get(self.question.id), self.answer)


# class AQPairsStore(object):
#     __tablename__ = "aqpairsstore"
#     id = db.Column(db.Integer, primary_key=True)
#     game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
#     question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
#     answer = db.Column(db.String(10))


class WhatMovieIsThat(Exception):
    def __str__(self):
        return "giveUp"

class IKnow(Exception):
    def __init__(self, movie):
        self.movie = movie

    def __str__(self):
        return u'Вы загадывали - "%s"?' % (self.movie)


class Game (db.Model):
    __tablename__ = "game"
    __number_of_played_games__ = 50
    __max_questions__ = 20
    id = db.Column(db.Integer, primary_key=True)
    # movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True)
    # answers = db.relationship("AQPairsStore", backref="game")
    X = None
    answers = {}
    elipson = 0.05
    pX = []

    def __init__(self):
        self.questions_counter = 0
        self.pX = numpy.ones(len(Movie.query.all()))
        self.connections = {}
        self.questions = Question.query.all()
        for q in self.questions:
            db.session.expunge(q)

        for q_id in [q.id for q in self.questions]:
            q_stats = QuestionWithStat.query.filter_by(question_id=q_id)
            self.connections[q_id] = [[], [], []]
            for q_stat in q_stats:
                total = q_stat.totalAnswers()
                if total != 0:
                    self.connections[q_id][0].append(q_stat.yes_answers / total)
                    self.connections[q_id][1].append(q_stat.no_answers / total)
                    self.connections[q_id][2].append(q_stat.idunno_answers / total)
                else:
                    self.connections[q_id][0].append(1/3)
                    self.connections[q_id][1].append(1/3)
                    self.connections[q_id][2].append(1/3)
        r_con = []
        for s in self.connections.items():
            r_con.append(s)

        self.movies = Movie.query.all()
        for m in self.movies:
            db.session.expunge(m)

        self.connections = r_con #yay!!
        print "connections: %s" % self.connections

    def get_next_question(self):
        if self.questions_counter < Game.__max_questions__:
            # self.pX = numpy.array([i.times_proposed for i in self.movies])
            current_entropy = entropy(self.pX)
            print "Entropy: " + str(current_entropy)

            for i, movie in enumerate(self.movies):
                print "%s  %s" % (movie, self.pX[i])

            if current_entropy < 1 or self.questions_counter == Game.__max_questions__ - 1:
                movie_index = self.pX.argmax()
                raise IKnow(self.movies[movie_index])

            else:

                pQA = numpy.tensordot(self.connections, self.pX, 1)
                print pQA
                self.pMQA = bayes(self.connections, self.pX, pQA)

                if numpy.random.random() < self.elipson:
                    print "Random Question:"
                    q = numpy.random.randint(len(self.questions))
                else:
                    entropys = entropy_after_answer(pQA, self.pMQA)
                    for q in self.answers.keys():
                        entropys[q] = numpy.inf
                    q = entropys.argmin()
                    self.last_q = q
                    print "Best Question: "
                question_to_ask = self.questions[q]
                return  question_to_ask
        else:
            if self.X is None:
                raise WhatMovieIsThat()
            else:
                self.update(self.answers, self.movie)

    def submit_next_answer(self, aq_pair):
        self.answers[aq_pair.question.id] = numpy.zeros(self.max_answers)
        if aq_pair.answer == Answers.YES:
            a = 0
        elif aq_pair.answer == Answers.NO:
            a = 1
        elif aq_pair.answer == Answers.I_DUNNO:
            a = 2

        self.answers[aq_pair.question.id][a] = 1
        self.pX = self.P_XQA[:, self.last_q, a]
        print u"add %s to game" % (aq_pair)

    def update(self, answers, item):
        for q in answers.keys():
            n = Game.__number_of_played_games__
            self.connections[q, :, item] *= (n - 1.) / n
            self.connections[q, :, item] += answers[q] / n
            # self.item_frequencies *= (n - 1.) / n
            self.item_frequencies[item] += 1. / n

    # def try_to_guess(self):
    #     movies = {}
    #     for m in Movie.query.all():
    #         movies[m.name] = str(self.countPWithActualAB(m, self.aq_pairs))
    #
    #     for k in movies:
    #         print u"%s : %s" % (k, movies[k])

    # def stop_with_answer(self, movie):
    #     Game.__number_of_played_games__ += 1
    #     for aqp in self.aq_pairs:
    #         q_stat = [s for s in movie.questions_stat if s.question == aqp.question][0]
    #         if q_stat != 0:
    #             q_stat.incrementWithAnswer(aqp)
    #         else:
    #             q_stat = QuestionWithStat()
    #             q_stat.question_id = aqp.question
    #             q_stat.movie_id = movie
    #             q_stat.incrementWithAnswer(aqp)
    #             db.session.add(q_stat)
    #             db.session.commit()


