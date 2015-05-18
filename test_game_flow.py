from app.models import *
from app.api import QuestionTypes
import requests
import numpy

print "Start new game!"

URL = "http://127.0.0.1:5000/api/v1.0/"

r = requests.get(URL + 'start_new_game/')

if r.status_code == 200:
    print r.json()
    game_id = r.json()['game_id']

    first = True
    rr = 0
    while(1):
        if first:
            question_type = r.json()['question_type']
            if question_type ==  QuestionTypes.COMMON.value:
                question = r.json()['question']
                print question
                ans = raw_input("y/n/idunno >     ")

                if ans == 'y':
                    answer = Answers.YES
                elif ans == 'n':
                    answer = Answers.NO
                elif ans == 'idunno':
                    answer = Answers.I_DUNNO

                data = {'game_id': game_id,
                        'answer': answer.value,
                        'question_type': QuestionTypes.COMMON.value,
                        'question_id': r.json()['question_id']}
                rr = requests.post(URL + 'submit_answer/', json=data)
                first = False

            elif question_type == QuestionTypes.FINAL:
                pass
            elif question_type == QuestionTypes.GIVE_UP:
                pass
        else:
            print rr.json()
            question_type = rr.json()['question_type']
            if question_type ==  QuestionTypes.COMMON.value:
                question = rr.json()['question']
                print question
                ans = raw_input("y/n/idunno >     ")

                if ans == 'y':
                    answer = Answers.YES
                elif ans == 'n':
                    answer = Answers.NO
                elif ans == 'idunno':
                    answer = Answers.I_DUNNO

                data = {'game_id': game_id,
                        'answer': answer.value,
                        'question_type': QuestionTypes.COMMON.value,
                        'question_id': rr.json()['question_id']}
                rr = requests.post(URL + 'submit_answer/', json=data)
            elif question_type == QuestionTypes.FINAL.value:
                # print numpy.array(rr.json()['movies'])
                movies = rr.json()['movies']
                for i, m in enumerate(movies):
                    print str(m) + "   " + str(i)

                ans = raw_input("Is it %s?   " % movies[0]['name'])
                if ans == 'y':
                    answer = Answers.YES
                    data = {'game_id': game_id,
                        'answer': answer.value,
                        'question_type': QuestionTypes.FINAL.value,
                        'movie_id': movies[0]['id']}
                    rr = requests.post(URL + 'submit_answer/', json=data)
                elif ans == 'n':
                    index = raw_input('Index of right answer >  ')

                    answer = Answers.YES
                    data = {'game_id': game_id,
                        'answer': answer.value,
                        'question_type': QuestionTypes.FINAL.value,
                        'movie_id': movies[int(index)]['id']}
                    rr = requests.post(URL + 'submit_answer/', json=data)
                break
            elif question_type == QuestionTypes.GIVE_UP.value:
                break
