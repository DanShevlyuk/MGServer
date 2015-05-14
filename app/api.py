from app import app, PATH
from flask import request, jsonify, abort
from app.models import Game, IKnow, WhatMovieIsThat, Question, Answers, AnswerQuestionPair, Movie
from datetime import datetime
from enum import Enum

active_games = {}

@app.route(PATH + 'start_new_game/', methods=['GET'])
def start_new_game():
    new_game  = Game()
    new_game_id = str(datetime.now())
    active_games[new_game_id] = new_game
    return jsonify(game_id=new_game_id), 200


class QuestionTypes(Enum):
    COMMON = 'simple'
    FINAL = 'final'
    GIVE_UP = 'give_up'

@app.route(PATH + 'get_next_question/', methods=['POST'])
def get_next_question():
    print request.json
    if not request.json or not ('game_id' in request.json):
        abort(400)

    game_id = request.json['game_id']

    if not (game_id in active_games.keys()):
        return jsonify(error='incorrect game_id!'), 404

    game = active_games[game_id]
    try:
        q_id = game.get_next_question()
    except IKnow as e:
        return jsonify(question_type=QuestionTypes.FINAL.value, question=e.movie.name), 200
    except WhatMovieIsThat as e:
        return jsonify(question_type=QuestionTypes.GIVE_UP.value), 200

    q = Question.query.get(q_id)

    return jsonify(question_type=QuestionTypes.COMMON.value, question=q.text, question_id=q.id), 200

@app.route(PATH + 'submit_answer/', methods=['POST'])
def submit_question():
    if not request.json or not (('game_id' and 'answer' and 'question_type') in request.json):
        abort(400)

    game_id = request.json['game_id']
    if not (game_id in active_games.keys()):
        return jsonify(error='incorrect game_id!'), 404

    game = active_games[game_id]
    question_id = request.json['question_id']
    answer = request.json['answer']
    question_type = request.json['question_type']

    if question_type == QuestionTypes.FINAL.value:
        if answer == Answers.YES.value:
            game.submit_final_answer(Answers.YES)
        elif answer == Answers.NO.value:
            game.submit_final_answer(Answers.NO)
        else:
            abort(400)
    elif question_type == QuestionTypes.GIVE_UP.value:
        if answer != '':
            movies = Movie.query.all()
            movies_from_base = [m for m in movies if m.name.lower() == answer.lower()]

            if len(movies_from_base):
                game.end_with_movie(movies_from_base[0].name)
                return jsonify(message='anther game done!'), 200
            else:
                print 'omg! new movie: %s' % answer
    elif question_type == QuestionTypes.COMMON.value:
        q = Question.query.get(question_id)
        if q is not None:
            game.submit_next_answer(AnswerQuestionPair(question=Question.query.get(question_id),
                                               answer=answer))
            return jsonify(message='awesome!'), 200
        else:
            return jsonify(message='incorrect question_id!'), 404

    return jsonify(message='awesome!'), 200

@app.route(PATH + 'get_all_movies/', methods=['GET'])
def get_all_movies():
    return jsonify(movies=[m.serialize() for m in Movie.query.all()]), 200

@app.route(PATH + 'get_all_questions/', methods=['GET'])
def get_all_questions():
    return jsonify(questions=[q.serialize() for q in Question.query.all()]), 200






