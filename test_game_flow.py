from app.models import *


print "Start new game!"

game = Game()
while(1):
    try:
        question = game.get_next_question()
    except IKnow as e:
        print "I think it's %s" % e.movie.name
        am_i_rigth = raw_input('Am I right? (y/n)   ')
        if am_i_rigth == 'y':
            game.submit_final_answer(Answers.YES)
        else:
            game.submit_final_answer(Answers.NO)
            continue
        break
    except WhatMovieIsThat as e:
        movie_name = raw_input('Oh man! I give up... What movie is that?   ')
        game.end_with_movie(str(movie_name))
        break

    print u"%s" % question

    ans = raw_input("y, n, idunno? >  ")


    answer = ''

    if ans == 'y':
        answer = Answers.YES
    elif ans =='n':
        answer == Answers.NO
    elif ans == 'idunno':
        answer == Answers.I_DUNNO
    else:
        assert Exception("Shit!")

    aq_pair = AnswerQuestionPair(question, answer)

    game.submit_next_answer(aq_pair)


