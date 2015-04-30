from enum import Enum

class Answers(Enum):
    YES = 1
    NO = 2
    DOES_NOT_MAKE_SENSE = 3
    HAVE_NO_IDEA = 4


class Movie(object):
    name = ""
    times_proposed = 0

    def __init__(self, name, times_proposed):
        self.name = name
        self.times_proposed = times_proposed


class Question(object):
    text = ""

    def __init__(self, text, ):
        self.text = text


class AnswerQuestionPair(object):
    question = Question()
    answer = Answers.YES

    def __init__(self, quesion, answer):
        self.question = quesion
        self.answer = answer
        

class Game(object):
    # static var
    __number_of_played_games__ = 0

    def __init__(self):
        print 'Yeah! New game!'

    def get_next_question(self):
        pass

    def submit_next_answer(self):
        pass

    def stop(self):
        pass

    def stop_with_answer(self):
        pass
