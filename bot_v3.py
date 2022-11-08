import os
import random
import time
import json
import asyncio
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv
from quiz_func import Quiz


# Open a xls file with quotes and ads them to the list that is used by a bot
df = pd.read_excel("static/cytaty.xls")
mylist = df['Listacytatow'].tolist()


# Dictionary to keep a list of contestants and their points
quiz_contestants = {}

# Assign Discord token kept in .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Assign "!" as a prefix to Discord commands
client = commands.Bot(command_prefix='!', intents = discord.Intents.all())


@client.command(name='konf', help='Displays a random quote from Confucius')
async def conf(ctx):
    """
    Function sends random Confucius quote
    """
    confucius_quote = mylist
    response = random.choice(confucius_quote)
    await ctx.send(response)


@client.command(name='quiz', help='Shows a general knowledge question.'\
    'You can receive points for guessing correctly!')
async def on_message(message):
    """
    Drawing and sending the question as a discord message
    """
    channel = message.channel
    quiz = Quiz()

    await channel.send("**Quiz Starting...**")
    time.sleep(1)
    await channel.send(quiz.question_content)
    await channel.send(quiz.question_answers())


    def check(msg):
        """
        Checking if author of answer was the person who used "!quiz" command
        """
        return msg.author == message.author
    try:
        # Setting the maximum annswer time to 60 seconds.
        guess = await client.wait_for('message', check=check , timeout=60.0)
    except asyncio.TimeoutError:
        await message.channel.send('Time is up')

    """
    If answer is given, program checks if it is the same as correct answer, if yes points are awarded accordingly.
    """
    if int(guess.content) == quiz.right_answer:
        await message.channel.send('**Correct answer**')
        nick = str(message.author)

        if nick not in quiz_contestants:
            quiz_contestants[nick] = 0
            quiz_contestants[nick] = quiz_contestants[nick]+1

        else:
            quiz_contestants[nick] = quiz_contestants[nick]+1

        new_points = quiz_contestants[nick]

        """
        Contestants dictionary is also added to contestants.txt file to be used as a backup.
        """
        with open("static/contestants.txt","w",encoding = 'utf-8') as file:
            file.write(json.dumps(quiz_contestants))

        if new_points == 1:
            points_message = f'Now **{nick}** has **{new_points} point**.'
        else:
            points_message = f'Now **{nick}** has **{new_points} points**.'

        await message.channel.send(points_message)

    else:
        await message.channel.send(f'Wrong answer, correct answer is **{quiz.answer[quiz.right_answer-1]}**')


@client.command(name='leaderboard', help='Shows current quiz leaderboard')
async def leaderboard(ctx):
    """
    Function to bring up a quiz leaderboard, results are sorted from highest to lowest
    """
    for key, val in sorted(quiz_contestants.items(), key=lambda x: x[1], reverse=True):
        player_stats = (f"{key}  {val}")
        await ctx.send(player_stats)


if __name__ == "__main__":
    client.run(TOKEN)
