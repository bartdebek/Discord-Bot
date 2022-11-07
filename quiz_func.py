import random
import json



class Quiz:
    """
    Class with attributes of random question drawn from json file
    """
    f = open("static/questionList.json")
    questions_list = json.load(f)
    questions_list = questions_list["trivia_questions"]

    def __init__(self):
        self.question_number = random.randint(0,len(self.questions_list)-1)
        self.question_content = self.questions_list[self.question_number]["question"]
        self.answer = self.questions_list[self.question_number]["answers"]
        self.right_answer = self.questions_list[self.question_number]["right_answer"]

    def question_answers(self):
        return f'1. **{self.answer[0]}** \n2. **{self.answer[1]}** \n'\
                        f'3. **{self.answer[2]}** \n4. **{self.answer[3]}**'
