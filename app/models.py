
# -*- coding: utf-8 -*-
from __future__ import division
from enum import Enum
from app import db
from utils.math_methods import entropy, entropy_after_answer
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

    def probability(self):
        return self.times_proposed / Game.__number_of_played_games__


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode(64), unique=False, nullable=False)
    questions_stat = db.relationship("QuestionWithStat", backref="question")

    def __unicode__(self):
        return u"%s" % (self.text)

    def getPQA(self):
        pQA = [0., 0. ,0.]
        for stat in self.questions_stat:
            current_pX = (stat.movie.times_proposed / Game.__number_of_played_games__)
            # current_pX = 0.1

            pQA[0] += stat.getPForAns(Answers.YES) * current_pX
            pQA[1] += stat.getPForAns(Answers.NO) * current_pX
            pQA[2] += stat.getPForAns(Answers.I_DUNNO) * current_pX


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
               self.idunno_answers

    def getAnswersAsDict(self):
        d = {}
        d[Answers.YES] = self.yes_answers
        d[Answers.NO] = self.no_answers
        d[Answers.I_DUNNO] = self.idunno_answers
        return d

    def getPForAns(self, ans):
        if self.totalAnswers() == 0:
            return 1/3
        else:
            ans_stat = 0
            if ans is Answers.YES:
                ans_stat = self.yes_answers
            elif ans is Answers.NO:
                ans_stat = self.no_answers
            elif ans is Answers.I_DUNNO:
                ans_stat = self.idunno_answers

            return ans_stat / self.totalAnswers()


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
    answers = []
    elipson = 0.05
    pX = {}
    last_pMQA = {}

    def __init__(self):
        self.questions_counter = 0
        self.questions = Question.query.all()
        for q in self.questions:
            db.session.expunge(q)

        self.movies = Movie.query.all()
        for m in self.movies:
            db.session.expunge(m)


    def get_next_question(self):
        # if self.questions_counter < Game.__max_questions__:
        if self.questions_counter < 5:
            # self.pX = numpy.array([i.times_proposed for i in self.movies])
            # pX = {}
            if len(self.pX) == 0:
                for m in Movie.query.all():
                    self.pX[m.id] = m.probability()

            print numpy.array(self.pX.values())
            current_entropy = entropy(numpy.array(self.pX.values()))
            print "Entropy: " + str(current_entropy)

            for i, movie in enumerate(self.movies):
                print u"%s  %s   id: %s" % (movie, self.pX[movie.id], movie.id)

            if current_entropy < 1 or self.questions_counter == 5 - 1:  # Game.__max_questions__ - 1:
                print "<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>"
                movie_array_index = numpy.array(self.pX.values()).argmax()
                # print "movie_id: %s" % movie_id
                p_to_search = (self.pX.values())[movie_array_index]
                movie = [m_id for m_id, p in self.pX.items() if p == p_to_search]
                if movie:
                    self.X = Movie.query.get(movie[0])
                    print "movie: %s" % self.X
                    raise IKnow(self.X)
                else:
                    print 'Shit!'
            else:
                if numpy.random.random() < self.elipson:
                    print "Random Question:"
                    qs = Question.query.all()
                    return qs[numpy.random.randint(len(qs))]
                else:
                    pQA = self.getPQA(self.pX)
                    # print "pQA: %s" % pQA
                    pMQA = self.bayes(pQA)
                    # print "pMQA: %s" % pMQA
                    self.last_pMQA = pMQA

                    entropys = entropy_after_answer(pQA, pMQA)
                    print "entropys: %s" % entropys
                    for q in self.answers:
                        entropys[q.question.id - 1] = numpy.inf
                    q = entropys.argmin()
                    print "Best Question: "
                question_to_ask = self.questions[q]
                self.questions_counter += 1
                return question_to_ask
        else:
            if self.X is None:
                raise WhatMovieIsThat()
            else:
                self.update(self.answers, self.movie)


    def bayes(self, pQA):
        res = {}
        for m in Movie.query.all():
            question_dict = {}
            for q_id, ps in pQA.iteritems():
                a_to_append = [0, 0, 0]
                qStat = QuestionWithStat.query.filter_by(movie_id=m.id, question_id=q_id).all()
                if len(qStat) != 0:
                    qStat = qStat[0]
                    a_to_append[0] = qStat.getPForAns(Answers.YES)
                    a_to_append[1] = qStat.getPForAns(Answers.NO)
                    a_to_append[2] = qStat.getPForAns(Answers.I_DUNNO)
                else:
                    a_to_append = [1/3, 1/3, 1/3]

                question_dict[q_id] = numpy.array(a_to_append)
            res[m.id] = question_dict

        return res

    def getPQA(self, pX):
        res = {}
        for q in Question.query.all():
            a_to_append = [0., 0. ,0.]
            for stat in q.questions_stat:
                # current_pX = (stat.movie.times_proposed / Game.__number_of_played_games__)
                # current_pX = 0.1
                current_pX = pX[stat.movie.id]

                a_to_append[0] += stat.getPForAns(Answers.YES) * current_pX
                a_to_append[1] += stat.getPForAns(Answers.NO) * current_pX
                a_to_append[2] += stat.getPForAns(Answers.I_DUNNO) * current_pX

            res[q.id] = numpy.array(a_to_append)

        return res

    def submit_next_answer(self, aq_pair):
        self.answers.append(aq_pair)
        q_index = 0
        if aq_pair.answer == Answers.YES:
            q_index = 0
        elif aq_pair.answer == Answers.NO:
            q_index = 1
        elif aq_pair.answer == Answers.I_DUNNO:
            q_index = 2

        self.pX = {}
        for m, qs in self.last_pMQA.iteritems():
             self.pX[m] = qs[aq_pair.question.id][q_index]
             print self.pX[m]

        print self.pX
        print u"add %s to game" % (aq_pair)

    def submit_final_answer(self, answer):
        if answer == Answers.YES:
            self.update(self.answers, self.X)
        elif answer == Answers.NO:
            self.questions_counter += 1
            self.pX[self.X.id] = 0
            self.X = None


    def update(self, answers, movie):
        Game.__number_of_played_games__ += 1
        movie.times_proposed += 1
        for aq_pair in answers:
            a = QuestionWithStat()
            a.question_id = aq_pair.question.id
            a.movie_id = movie.id
            if aq_pair.answer == Answers.YES:
                a.yes_answers += 1
            elif aq_pair.answer == Answers.NO:
                a.no_answers += 1
            elif aq_pair.answer == Answers.I_DUNNO:
                a.idunno_answers += 1

            db.session.add(a)
            db.session.commit()

        db.session.add(movie)
        db.session.commit()


    def end_with_movie(self, movie_name):
        movies = Movie.query.filter_by(name=movie_name).all()

        if len(movies) == 0:
            print 'omg! new movie.'
        else:
            self.update(self.answers, movies[0])



