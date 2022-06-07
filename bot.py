from multiprocessing.connection import Client
import os
import random
import json
import pandas as pd
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Open a xls file with quotes and ads them to the list that is used by a bot

df = pd.read_excel("Static/cytaty.xls") 
cytaty_konfucjusza = df['Listacytatow'].tolist()

df = pd.read_excel("Static/pozytywy.xls") 
pozytywne_cytaty = df['Listacytatow'].tolist()

# Dictionary to keep a list of contestants and their points

quizContestants = {} 

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

quizContestants = {}

# Open a file with quiz questions

f = open("Static/questionList.json") 
questionsList = json.load(f)
questionsList = questionsList["trivia_questions"]

def question_draw():
    """Function that draws a quiz question number to be asked when used with !quiz command"""

    question_number = random.randint(0,len(questionsList)-1)
    right_answer = questionsList[question_number]["right_answer"]

    return question_number,right_answer

class Question():
    
    def __init__(self,question_number,right_answer) -> None:
        self.question_number = question_number
        self.right_answer = right_answer

    def __str__(self):
        return (f"Question: {questionsList[self.question_number]['question']}\n\n"
f"1. {questionsList[self.question_number]['answers'][0]}\n"
f"2. {questionsList[self.question_number]['answers'][1]}\n"
f"3. {questionsList[self.question_number]['answers'][2]}\n"
f"4. {questionsList[self.question_number]['answers'][3]}\n")

    def get_right_answer(self):
        return(f"{questionsList[self.question_number]['answers'][self.right_answer-1]}")

# Commands to send a random question to the person that send "!quiz" message.

@client.command(name='quiz', help='Shows a general knowledge question. You can receive points for guessing correctly!')
async def on_message(message):
    channel = message.channel

# Drawing and sending the question as a discord message

    random_question = question_draw()
    chosen_question = Question(random_question[0],random_question[1])
    await channel.send(chosen_question)
    right_answer = random_question[1]

# Checking if author of answer was the person who used "!quiz" command, 
# setting the maximum annswer time to 60 seconds. 

    def check(m):
        return m.author == message.author
    try:
        guess = await client.wait_for('message', check=check , timeout=60.0)
    except asyncio.TimeoutError:
        await message.channel.send('Time is up')

# If answer is given, program checks if it is the same as correct answer, if yes points are awarded accordingly. 

    if int(guess.content) == right_answer:
        await message.channel.send('Correct answer')
        nick = str(message.author)
        
        if nick not in quizContestants:
            quizContestants[nick] = 0
            quizContestants[nick] = quizContestants[nick]+1

        else:
            quizContestants[nick] = quizContestants[nick]+1

        newPoints = quizContestants[nick]

# Contestants dictionary is also added to contestants.txt file to be used as a backup  

        with open("Static/contestants.txt","w") as file:
            file.write(json.dumps(quizContestants))
        pointsMessage = (f'Now {nick} has {newPoints} points.')
        await message.channel.send(pointsMessage)

    else:
        await message.channel.send(f'Wrong answer, correct answer is {chosen_question.get_right_answer()}')
        print(right_answer)
    
# Command brings up a quiz leaderboard

@client.command(name='leaderboard', help='Shows current quiz leaderboard')
async def leaderboard(ctx):
    for key, val in quizContestants.items():
        x = (f"{key}  {val}")
        await ctx.send(x)


client.run(TOKEN)