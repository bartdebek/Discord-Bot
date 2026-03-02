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
        self.question = random.choice(self.questions_list)
        self.question_content = self.question["question"]
        self.answer = self.question["answers"]
        self.right_answer = self.question["right_answer"]

    def question_answers(self):
        """Method to return answers in a format for quiz"""
        return (
            f"1. **{self.answer[0]}** \n2. **{self.answer[1]}** \n"
            f"3. **{self.answer[2]}** \n4. **{self.answer[3]}**"
        )
