from app import app, PATH
from flask import request, jsonify, abort
from app.models import Game, IKnow, Question, Answers, AnswerQuestionPair, Movie
from datetime import datetime
from enum import Enum

active_games = {}

@app.route(PATH + 'start_new_game/', methods=['GET'])
def start_new_game():
    new_game = Game()
    new_game_id = str(datetime.now())
    active_games[new_game_id] = new_game
    try:
        q = new_game.get_next_question()
    except IKnow as e:
        return jsonify(game_id=new_game_id,
                       question_type=QuestionTypes.FINAL.value,
                       movies=[m.serialize() for m in e.movie_list]), 200
    # except WhatMovieIsThat as e:
    #     return jsonify(game_id=new_game_id, question_type=QuestionTypes.GIVE_UP.value), 200


    return jsonify(game_id=new_game_id,
                   question=q.text,
                   question_type=QuestionTypes.COMMON.value,
                   question_id=q.id), 200


class QuestionTypes(Enum):
    COMMON = 'common'
    FINAL = 'final'
    # GIVE_UP = 'give_up'

# @app.route(PATH + 'get_next_question/', methods=['GET'])
def get_next_question(game):
    try:
        question = game.get_next_question()
    except IKnow as e:
        return jsonify(question_type=QuestionTypes.FINAL.value,
                       movies=[Movie.query.get(m).serialize() for m in e.movie_list]), 200
    # except WhatMovieIsThat as e:
    #     return jsonify(question_type=QuestionTypes.GIVE_UP.value), 200

    return jsonify(question_type=QuestionTypes.COMMON.value, question=question.text, question_id=question.id), 200

@app.route(PATH + 'submit_answer/', methods=['POST'])
def submit_answer():
    if not request.json or not (('game_id' and 'answer' and 'question_type') in request.json):
        abort(400)

    game_id = request.json['game_id']
    if not (game_id in active_games.keys()):
        return jsonify(error='incorrect game_id!'), 404

    game = active_games[game_id]
    answer = request.json['answer']
    question_type = request.json['question_type']

    if question_type == QuestionTypes.FINAL.value:
        movie_id = request.json['movie_id']
        if answer == Answers.YES.value:
            game.submit_final_answer(movie_id, Answers.YES)
            return jsonify(message="awesome"), 200
        elif answer == Answers.NO.value:
            game.submit_final_answer(Answers .NO)
        else:
            abort(400)
    # elif question_type == QuestionTypes.GIVE_UP.value:
    #     if answer != '':
    #         movies = Movie.query.all()
    #         movies_from_base = [m for m in movies if m.name.lower() == answer.lower()]
    #
    #         if len(movies_from_base):
    #             game.end_with_movie(movies_from_base[0].name)
    #             return jsonify(message='anther game done!'), 200
    #         else:
    #             print 'omg! new movie: %s' % answer
    elif question_type == QuestionTypes.COMMON.value:
        question_id = request.json['question_id']
        q = Question.query.get(question_id)
        if q is not None:
            game.submit_next_answer(AnswerQuestionPair(question_id=question_id,
                                               answer=answer))
        else:
            return jsonify(message='incorrect question_id!'), 404

    return get_next_question(game)

@app.route(PATH + 'get_all_movies/', methods=['GET'])
def get_all_movies():
    return jsonify(movies=[m.serialize() for m in Movie.query.all()]), 200

@app.route(PATH + 'get_all_questions/', methods=['GET'])
def get_all_questions():
    return jsonify(questions=[q.serialize() for q in Question.query.all()]), 200

@app.route(PATH + 'get_active_sessions/', methods=['GET'])
def get_active_sessions():
    return jsonify(games=active_games.keys()), 200

@app.route(PATH + 'kill_all_games/', methods=['DELETE'])
def kill_all_games():
    active_games.clear()
    return 'ok!', 200

@app.route(PATH + 'kill_game/', methods=['DELETE'])
def kill_game():
    if not request.json or not ('game_id' in request.json):
        abort(400)
    del active_games[request.json['game_id']]
    return 'ok!', 200

@app.route(PATH + 'submit_new_movie/', methods=['POST'])
def submit_new_movie():
    if not request.json or not ('movie_name' in request.json):
        abort(400)

    print request.json['movie_name']

@app.route(PATH + 'submit_new_question/', methods=['POST'])
def submit_new_question():
    if not request.json or not ('question' in request.json):
        abort(400)

    print request.json['question']

@app.route(PATH + 'report/', methods=['POST'])
def report():
    if not request.json or not ('text' in request.json):
        abort(400)

