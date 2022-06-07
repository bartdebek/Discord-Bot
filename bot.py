# bot.py
from multiprocessing.connection import Client
import os
import random
import json
import pandas as pd
import asyncio
from discord.ext import commands
from dotenv import load_dotenv



# Open a xls file with quotes and ads them to the list that is used by a bot

df = pd.read_excel("Discord bot\cytaty.xls") 
mylist = df['Listacytatow'].tolist()


# Dictionary to keep a list of contestants and their points

quizContestants = {} 

def question_draw():
    """Function that draws a quiz question number to be asked when used with !quiz command"""

    question_number = random.randint(0,len(questionsList)-1)
    return question_number


# Assign Discord token kept in .env file

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') 

# Open a file with quiz questions

f = open("questionsJson3.json") 
questionsList = json.load(f)
questionsList = questionsList["trivia_questions"]
    
# Assign "!" as a prefix to Discord commands
client = commands.Bot(command_prefix='!')

# Commands to send a random quote from Confucius

@client.command(name='konf', help='Displays a random quote from Confucius')
async def janusz(ctx):
    cytaty_korwina = mylist

    response = random.choice(cytaty_korwina)
    await ctx.send(response)


# Commands to send a random question to the person that send "!quiz" message.

@client.command(name='kwiz', help='Shows a general knowledge question. You can receive points for guessing correctly!')
async def on_message(message):
    channel = message.channel

# Drawing and sending the question as a discord message

    QuestNumber = question_draw()
    await channel.send("Quiz Starting...")
    await channel.send(questionsList[QuestNumber]["question"])
    await channel.send(f'\n1. {questionsList[QuestNumber]["answers"][0]}\n2. {questionsList[QuestNumber]["answers"][1]} \n3. {questionsList[QuestNumber]["answers"][2]} \n4. {questionsList[QuestNumber]["answers"][3]}')
    rightAnswer = questionsList[QuestNumber]["right_answer"]

# Checking if author of answer was the person who used "!quiz" command, 
# setting the maximum annswer time to 60 seconds. 

    def check(m):
        return m.author == message.author
    try:
        guess = await client.wait_for('message', check=check , timeout=60.0)
    except asyncio.TimeoutError:
        await message.channel.send('Time is up')

# If answer is given, program checks if it is the same as correct answer, if yes points are awarded
# accordingly. Contestants dictionary is also added to contestants.txt file to be used as a backup  

    if int(guess.content) == rightAnswer:
        await message.channel.send('Correct answer')
        nick = str(message.author)
        if nick not in quizContestants:
            quizContestants[nick] = 0
            quizContestants[nick] = quizContestants[nick]+1
        else:
            quizContestants[nick] = quizContestants[nick]+1
        newPoints = quizContestants[nick]
        with open("contestants.txt","w") as file:
            file.write(json.dumps(quizContestants))
        pointsMessage = ("Now {} has {} points.".format(nick,newPoints))
        await message.channel.send(pointsMessage)

    else:
        await message.channel.send('Wrong answer, correct answer is {}'.format(questionsList[QuestNumber]["answers"][rightAnswer-1]))
        print(rightAnswer)
    
# Command brings up a quiz leaderboard

@client.command(name='leaderboard', help='Shows current quiz leaderboard')
async def leaderboard(ctx):
    for key, val in quizContestants.items():
        x = "{}  {}".format(key,val)
        await ctx.send(x)


client.run(TOKEN)