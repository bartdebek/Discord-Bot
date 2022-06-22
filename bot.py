import os
import random
import json
import asyncio
import pandas as pd
from discord.ext import commands
from dotenv import load_dotenv

# Open a xls file with quotes and ads them to the list that is used by a bot

df = pd.read_excel("Static/cytaty.xls")
cytaty_konfucjusza = df['Listacytatow'].tolist()

df = pd.read_excel("Static/pozytywy.xls")
pozytywne_cytaty = df['Listacytatow'].tolist()

# Dictionary to keep a list of contestants and their points

quiz_contestants = {}

# Assign Discord token kept in .env file

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Assign "!" as a prefix to Discord commands
client = commands.Bot(command_prefix='!')

# Commands to send a random quote from Confucius

@client.command(name='konf', help='Displays a random quote from Confucius')
async def janusz(ctx):
    quoteset = cytaty_konfucjusza
    response = random.choice(quoteset)
    await ctx.send(response)

# Commands to send a random positive quote

@client.command(name='poz', help='Displays a positive quote to cheer you up!')
async def poz(ctx):
    quoteset = pozytywne_cytaty
    response = random.choice(quoteset)
    await ctx.send(response)

# Defining functions to draw a question and then pront it out

quiz_contestants = {}

# Open a file with quiz questions

with open("Static/questionList.json","r",encoding = 'utf-8') as f:
    questions_list = json.load(f)
    questions_list = questions_list["trivia_questions"]

def question_draw():
    """Function that draws a quiz question number
    to be asked when used with !quiz command"""

    question_number = random.randrange(len(questions_list)-1)
    right_answer = questions_list[question_number]["right_answer"]
    right_answer_text = questions_list[question_number]['answers'][right_answer-1]

    return question_number, right_answer, right_answer_text

# QUESTION CLASS

class Question():

    def __init__(self,question_number, right_answer, right_answer_text):
        self.question_number = question_number
        self.right_answer = right_answer
        self.right_answer_text = right_answer_text

    def __str__(self):
        return (f"Question: {questions_list[self.question_number]['question']}\n\n"
        f"1. {questions_list[self.question_number]['answers'][0]}\n"
        f"2. {questions_list[self.question_number]['answers'][1]}\n"
        f"3. {questions_list[self.question_number]['answers'][2]}\n"
        f"4. {questions_list[self.question_number]['answers'][3]}\n")

    def get_right_answer(self):
        return f"{self.right_answer_text}"

# Commands to send a random question to the person that send "!quiz" message.

@client.command(name='quiz',
help='Shows a general knowledge question. You can receive points for guessing correctly!')

async def on_message(message):
    channel = message.channel

# Drawing and sending the question as a discord message

    random_question = question_draw()
    chosen_question = Question(random_question[0],random_question[1],random_question[2])
    await channel.send(chosen_question)
    right_answer = random_question[1]

# Checking if author of answer was the person who used "!quiz" command,
# setting the maximum annswer time to 60 seconds.

    def check(mes):
        return mes.author == message.author
    try:
        guess = await client.wait_for('message', check=check , timeout=60.0)
    except asyncio.TimeoutError:
        await message.channel.send('Time is up')

# If answer is given, program checks if it is the same as correct answer,
# if yes points are awarded accordingly.

    if int(guess.content) == right_answer:
        await message.channel.send('Correct answer')
        nick = str(message.author)
        if nick not in quiz_contestants:
            quiz_contestants[nick] = 1
        else:
            quiz_contestants[nick] = quiz_contestants[nick]+1

        new_points = quiz_contestants[nick]

# Contestants dictionary is also added to contestants.txt file to be used as a backup

        with open("Static/contestants.txt","w",encoding = 'utf-8') as file:
            file.write(json.dumps(quiz_contestants))
        points_message = (f'Now {nick} has {new_points} points.')
        await message.channel.send(points_message)

    else:
        await message.channel.send(
            f'Wrong answer, correct answer is {chosen_question.get_right_answer()}'
            )

# Command brings up a quiz leaderboard

@client.command(name='leaderboard', help='Shows current quiz leaderboard')
async def leaderboard(ctx):
    for key, val in quiz_contestants.items():
        leaderboard_message = f"{key}  {val}"
        await ctx.send(leaderboard_message)


client.run(TOKEN)
