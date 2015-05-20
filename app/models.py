# -*- coding: utf-8 -*-
from __future__ import division
from enum import Enum
from app import db
from utils.math_methods import entropy, entropy_after_answer
from collections import OrderedDict
import numpy
import operator
# import psyco

# psyco.jit()


class Answers(Enum):
    YES = 'yes'
    NO = 'no'
    I_DUNNO = 'I dunno'


class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True)
    times_proposed = db.Column(db.Integer)
    questions_stat = db.relationship("QuestionWithStat", backref="movie")

    def __init__(self, name):
        self.name = name
        self.times_proposed = 1.

    def __unicode__(self):
        return u"%s" % (self.name)

    def probability(self):
        return self.times_proposed / Game.__number_of_played_games__

    def serialize(self):
        return {
            'id' : self.id,
            'name': self.name,
            'times_proposed': self.times_proposed
        }


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

    def serialize(self):
        stat = self.questions_stat
        total_answers = 0
        for s in stat:
            total_answers += s.totalAnswers()

        return {
            'id' : self.id,
            'text': self.text,
            'total_answers': total_answers
        }



class QuestionWithStat(db.Model):
    __tablename__ = "questionwithstat"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    yes_answers = db.Column(db.Integer)
    no_answers = db.Column(db.Integer)
    idunno_answers = db.Column(db.Integer)

    def __init__(self):
        self.yes_answers = 1
        self.no_answers = 1
        self.idunno_answers = 1

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
        ans_stat = 0
        if ans is Answers.YES:
            ans_stat = self.yes_answers
        elif ans is Answers.NO:
            ans_stat = self.no_answers
        elif ans is Answers.I_DUNNO:
            ans_stat = self.idunno_answers

        if self.totalAnswers() == 0:
            return 1/3

        return ans_stat / self.totalAnswers()


class AnswerQuestionPair(object):
    def __init__(self, question_id, answer):
        self.question_id = question_id
        self.answer = answer

    def __unicode__(self):
        return u"'%s' >>> %s" % (Question.query.get(self.question_id), self.answer)

#
# class WhatMovieIsThat(Exception):
#     def __str__(self):
#         return "giveUp"


class IKnow(Exception):
    def __init__(self, m_list):
        self.movie_list = m_list

    def __str__(self):
        return u'"%s"?' % (Movie.quesry.get(self.movie_list[0]))


# psyco.bind(Game)

class Game (object):
    # __tablename__ = "game"
    __number_of_played_games__ = sum([m.times_proposed for m in Movie.query.all()])
    __max_questions__ = 5
    # id = db.Column(db.Integer, primary_key=True)
    # movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True)
    # answers = db.relationship("AQPairsStore", backref="game")
    X = None
    answers = {}
    pX = {}
    elipson = 0.05
    last_pMQA = {}

    def __init__(self):
        self.questions_counter = 0
        self.answers = {}
        self.pX = {}

        for m in Movie.query.all():
            self.pX[m.id] = m.probability()
            # db.session.expunge(m)

        self.questions = Question.query.all()
        # for q in self.questions:
        #     db.session.expunge(q)
        #
        # self.movies = Movie.query.all()
        # for m in self.movies:
        #     db.session.expunge(m)


    def get_next_question(self):
        # if self.questions_counter < Game.__max_questions__:
        current_entropy = entropy(numpy.array(self.pX.values()))
        # print "Entropy: " + str(current_entropy)

        for i, movie in enumerate(Movie.query.all()):
            print u"%s  %s" % (movie, self.pX[movie.id])

        if current_entropy < 1 or self.questions_counter == Game.__max_questions__:
        # if current_entropy < 1 or self.questions_counter == len(Question.query.all()) - 1:
        #     print "<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>"
            sorted_pX = sorted(self.pX.items(), key=operator.itemgetter(1), reverse=True)
            sorted_pX = [sorted_pX[i][0] for i in xrange(len(sorted_pX))]
            self.X = sorted_pX[0]
            # print sorted_pX
            raise IKnow(sorted_pX)

        else:
            if numpy.random.random() < self.elipson:
                # print "Random Question:"
                qs = Question.query.all()
                qs = [q for q in qs if not (q.id in self.answers.keys())]
                self.questions_counter += 1
                return qs[numpy.random.randint(len(qs))]
            else:
                pQA = self.getPQA()
                pMQA = self.bayes(pQA)
                self.last_pMQA = pMQA

                entropys = entropy_after_answer(pQA, pMQA)
                for q in self.answers.keys():
                    entropys[q - 1] = numpy.inf

                q = entropys.argmin()
                # print "Best Question: "
                question_to_ask = Question.query.get(q+1)
                self.questions_counter += 1
                return question_to_ask
        # else:
        #     if self.X is None:
        #         raise WhatMovieIsThat()
        #     else:
        #         self.update(self.answers, self.X)

    def bayes(self, pQA):
        res = {}
        for m in Movie.query.all():
            question_dict = {}
            for q_id, ps in pQA.iteritems():
                a_to_append = numpy.zeros(3)
                qStat = QuestionWithStat.query.filter_by(movie_id=m.id, question_id=q_id).first()
                if qStat:
                    a_to_append[0] = qStat.getPForAns(Answers.YES)
                    a_to_append[1] = qStat.getPForAns(Answers.NO)
                    a_to_append[2] = qStat.getPForAns(Answers.I_DUNNO)
                else:
                    a_to_append = numpy.array([1/3, 1/3, 1/3])

                question_dict[q_id] = a_to_append
            res[m.id] = question_dict

        return res

    def getPQA(self):
        res = {}
        for q in Question.query.all():
            a_to_append = numpy.zeros(3)
            for stat in q.questions_stat:
                current_pX = self.pX[stat.movie.id]

                a_to_append[0] += stat.getPForAns(Answers.YES) * current_pX
                a_to_append[1] += stat.getPForAns(Answers.NO) * current_pX
                a_to_append[2] += stat.getPForAns(Answers.I_DUNNO) * current_pX

            res[q.id] = a_to_append

        return res

    def submit_next_answer(self, aq_pair):
        self.answers[aq_pair.question_id] = aq_pair.answer
        q_index = 0
        if aq_pair.answer == Answers.YES:
            q_index = 0
        elif aq_pair.answer == Answers.NO:
            q_index = 1
        elif aq_pair.answer == Answers.I_DUNNO:
            q_index = 2

        self.pX = {}
        for m, qs in self.last_pMQA.iteritems():
             self.pX[m] = qs[aq_pair.question_id][q_index]


    def submit_final_answer(self, movie_id, answer):
        if answer == Answers.YES:
            self.update(self.answers, movie_id)
        # elif answer == Answers.NO:
        #     #==========================================================================================
        #     self.questions_counter += 1
        #     self.pX[self.X.id] = 0
        #     self.X = None


    def update(self, answers, movie_id):
        Game.__number_of_played_games__ += 1
        movie = Movie.query.get(movie_id)
        movie.times_proposed += 1
        for q_id, ans in answers.iteritems():
            a = QuestionWithStat()
            a.question = Question.query.get(q_id)
            a.movie = Movie.query.get(movie.id)
            if ans == Answers.YES:
                a.yes_answers += 1
            elif ans == Answers.NO:
                a.no_answers += 1
            elif ans == Answers.I_DUNNO:
                a.idunno_answers += 1

            db.session.add(a)
            db.session.commit()
        db.session.add(movie)
        db.session.commit()

    def end_with_movie(self, movie_id):
        movie = Movie.query.get(movie_id)
        if movie:
            self.update(self.answers, movie_id)


