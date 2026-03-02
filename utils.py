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


class Player:
    """
    Class with attributes of player and simple JSON persistence.

    Each instance can serialize itself to `STORAGE` and the class can
    load all existing records.  Methods that mutate state call `save`
    so the file is kept up to date whenever points or answers change.
    """

    STORAGE = "static/contestants.json"

    def __init__(self, name, data=None):
        self.name = name
        self.points = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        if data:
            self.load_from_dict(data)


    def load_from_dict(self, data):
        """Method to load player data from dictionary"""
        self.points = data.get("points", 0)
        self.correct_answers = data.get("correct_answers", 0)
        self.wrong_answers = data.get("wrong_answers", 0)

    def add_points(self):
        """Method to add points to player"""
        self.points += 1
        self.correct_answers += 1
        # persist the updated player data immediately
        self.save()

    def add_wrong_answer(self):
        """Method to add wrong answer to player"""
        self.wrong_answers += 1
        # update the stored json as well
        self.save()

    def success_rate(self):
        """Method to calculate player's success rate"""
        total_answers = self.correct_answers + self.wrong_answers
        if total_answers == 0:
            return 0
        return (self.correct_answers / total_answers) * 100

    def to_dict(self):
        """Return a plain dict suitable for JSON serialization."""
        return {
            "name": self.name,
            "points": self.points,
            "correct_answers": self.correct_answers,
            "wrong_answers": self.wrong_answers,
        }

    @classmethod
    def load_all(cls):
        """Read all players from the storage file and return objects.

        The historical format was a mapping from name -> stats, so we
        normalize either structure into a list of dictionaries.  Corrupt
        or missing files simply return an empty list.
        """
        try:
            with open(cls.STORAGE, encoding="utf-8") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        # migrate old dict-of-dicts format
        if isinstance(raw, dict):
            records = []
            for name, stats in raw.items():
                entry = {"name": name}
                if isinstance(stats, dict):
                    entry.update(stats)
                records.append(entry)
        elif isinstance(raw, list):
            records = raw
        else:
            # unexpected type, give up
            return []

        return [cls(item.get("name"), item) for item in records]

    def save(self):
        """Persist this player to disk, adding or updating the record."""
        players = self.load_all()
        for existing in players:
            if existing.name == self.name:
                existing.points = self.points
                existing.correct_answers = self.correct_answers
                existing.wrong_answers = self.wrong_answers
                break
        else:
            players.append(self)
        with open(self.STORAGE, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in players], f, indent=2)

    def __str__(self):
        return f"**{self.name} lifetime stats:**\n**{self.points}** points\n**{self.correct_answers}** correct answers\n**{self.wrong_answers}** wrong answers\n**{self.success_rate():.2f}%** success rate"