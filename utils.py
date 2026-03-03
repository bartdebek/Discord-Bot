import random
import json

from consts import QUESTION_MODAL, QUESTION_BUTTONS

# discord.py is optional for non-bot code (tests, etc.).  import it only if
# available so that `Quiz` can be used without installing the package.
try:
    import discord
    from discord import ui, TextStyle
except ImportError:  # tests may run on a machine without discord
    discord = None
    ui = None
    TextStyle = None



# Only define Discord-related helpers when the library is present.  The
# remainder of this file (Quiz, Player) works in plain Python, which makes
# it safe to import in unit tests or other non-bot contexts.

if discord is not None:
    class QuizModal(ui.Modal):
        """Build a modal from the JSON template in ``consts.py``.

        The constant lives in data so you can tweak the fields in JSON rather
        than rewriting Python.  During initialization we format the template
        with the current question/answers, parse it and translate each text
        input entry into a ``discord.ui.TextInput`` item.  The ``on_submit``
        handler (defined later) still contains the evaluation logic.
        """

        def __init__(self, quiz: "Quiz"):
            # format the template with concrete quiz values and parse it
            raw = QUESTION_MODAL.format(
                question=quiz.question_content,
                answer0=quiz.answer[0],
                answer1=quiz.answer[1],
                answer2=quiz.answer[2],
                answer3=quiz.answer[3],
            )
            spec = json.loads(raw)
            info = spec[0]  # our templating uses a single-object list

            # pass along title/custom_id if provided
            title = info.get("title", "Quiz question")
            super().__init__(title=title, custom_id=info.get("custom_id"))
            self.quiz = quiz

            # walk the component hierarchy and add text inputs
            for row in info.get("components", []):
                for comp in row.get("components", []):
                    if comp.get("type") == 4:  # text input
                        style = TextStyle.long if comp.get("style") == 2 else TextStyle.short
                        ti = ui.TextInput(
                            label=comp.get("label", ""),
                            style=style,
                            required=not comp.get("disabled", False),
                            custom_id=comp.get("custom_id"),
                            default=comp.get("value", ""),
                            placeholder=comp.get("placeholder", ""),
                            max_length=comp.get("max_length"),
                            min_length=comp.get("min_length"),
                        )
                        if comp.get("disabled", False):
                            ti.disabled = True
                        self.add_item(ti)
                        if comp.get("custom_id") == "answer":
                            # keep a reference so on_submit can look at it
                            self.answer_input = ti

    async def on_submit(self, interaction: discord.Interaction):
        """Called when the user submits the modal."""
        # evaluate the answer and update points just like the old command
        try:
            guess = int(self.answer_input.value)
        except ValueError:
            await interaction.response.send_message(
                "Please enter a number between 1 and 4.", ephemeral=True
            )
            return

        player = None
        # importing here to avoid circular import problems; bot_v3
        # defines get_player and quiz_contestants, so we import them
        from bot_v3 import get_player, quiz_contestants

        if guess == self.quiz.right_answer:
            nick = str(interaction.user)
            player = get_player(nick)
            player.add_points()
            with open("static/contestants.json", "w", encoding="utf-8") as file:
                file.write(json.dumps([p.to_dict() for p in quiz_contestants]))

            if player.points == 1:
                points_message = f"Now **{nick}** has **{player.points} point**."
            else:
                points_message = f"Now **{nick}** has **{player.points} points**."

            await interaction.response.send_message("**Correct answer**\n" + points_message)
        else:
            nick = str(interaction.user)
            player = get_player(nick)
            player.add_wrong_answer()
            correct = self.quiz.answer[self.quiz.right_answer - 1]
            await interaction.response.send_message(
                f"Wrong answer, correct answer is **{correct}**"
            )





if discord is not None:
    class QuizView(ui.View):
        """A view containing answer buttons and optional media.

        The layout is defined by the ``QUESTION_BUTTONS`` JSON template in
        *consts.py*.  At construction the template is formatted with the
        current ``Quiz`` instance; we then parse the resulting JSON and create
        a button for each entry.  The ``author`` parameter is used to prevent
        other users from answering someone else's quiz.
        """

        def __init__(self, quiz: "Quiz", author: discord.abc.User):
            super().__init__(timeout=60.0)
            self.quiz = quiz
            self.author = author
            self.embed = None

            raw = QUESTION_BUTTONS.format(
                question=quiz.question_content,
                answer0=quiz.answer[0],
                answer1=quiz.answer[1],
                answer2=quiz.answer[2],
                answer3=quiz.answer[3],
            )
            spec = json.loads(raw)[0]

            # extract optional media for an embed
            media_url = None
            for row in spec.get("components", []):
                if row.get("type") == 9:  # accessory row
                    acc = row.get("accessory", {})
                    if acc.get("type") == 11:
                        media_url = acc.get("media", {}).get("url")
            if media_url:
                self.embed = discord.Embed(description=quiz.question_content)
                self.embed.set_thumbnail(url=media_url)

            # create buttons
            for row in spec.get("components", []):
                if row.get("type") == 1:  # action row
                    for comp in row.get("components", []):
                        if comp.get("type") == 2:  # button
                            label = comp.get("label", "")
                            cid = comp.get("custom_id")
                            raw_style = comp.get("style", 1)
                            # the json holds an integer; convert to ButtonStyle enum
                            try:
                                style = discord.ButtonStyle(raw_style)
                            except Exception:
                                style = discord.ButtonStyle.primary
                            button = ui.Button(label=label, custom_id=cid, style=style)
                            # attach callback that closes over this view
                            async def make_callback(interaction=discord.Interaction, index=cid):
                                # ignore other users
                                if interaction.user != self.author:
                                    await interaction.response.send_message(
                                        "This quiz isn't for you.", ephemeral=True
                                    )
                                    return
                                # custom_id from JSON was '0'..'3', but
                                # right_answer is 1‑based.  convert accordingly.
                                guess = int(index) + 1
                                from bot_v3 import get_player, quiz_contestants
                                if guess == self.quiz.right_answer:
                                    nick = str(interaction.user)
                                    player = get_player(nick)
                                    player.add_points()
                                    with open("static/contestants.json", "w", encoding="utf-8") as f:
                                        f.write(json.dumps([p.to_dict() for p in quiz_contestants]))
                                    if player.points == 1:
                                        pts = "point"
                                    else:
                                        pts = "points"
                                    response_text = (
                                        f"**Correct answer**\nNow **{nick}** has **{player.points} {pts}**."
                                    )
                                else:
                                    nick = str(interaction.user)
                                    player = get_player(nick)
                                    player.add_wrong_answer()
                                    correct = self.quiz.answer[self.quiz.right_answer - 1]
                                    response_text = f"Wrong answer, correct answer is **{correct}**"
                                # disable all buttons after answer
                                for child in self.children:
                                    child.disabled = True
                                await interaction.response.edit_message(view=self)
                                # edit the original message with the result and disabled view
                                await interaction.channel.send(response_text)

                                self.stop()
                        button.callback = make_callback
                        self.add_item(button)



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
    def question_modal(self):
        return QUESTION_MODAL.format(
            question=self.question_content,
            answer0=self.answer[0],
            answer1=self.answer[1],
            answer2=self.answer[2],
            answer3=self.answer[3]
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
        print(f"DEBUG: Loading player data for {self.name} from dict: {data}")
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