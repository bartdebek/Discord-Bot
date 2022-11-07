import os
import random
import time
import json
import pandas as pd
import asyncio
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

# Commands to send a random quote from Confucius
@client.command(name='konf', help='Displays a random quote from Confucius')
async def conf(ctx):
    cytaty_konfucjusza = mylist

    response = random.choice(cytaty_konfucjusza)
    await ctx.send(response)


# Commands to send a random question to the person that send "!quiz" message.
@client.command(name='quiz', help='Shows a general knowledge question. You can receive points for guessing correctly!')
async def on_message(message):
    channel = message.channel

# Drawing and sending the question as a discord message

    quiz = Quiz()
    QuestNumber = quiz.question_draw()
    question_content = quiz.questions_list[QuestNumber]["question"]
    answer = quiz.questions_list[QuestNumber]["answers"]
    question_answers = f'1. **{answer[0]}** \n2. **{answer[1]}** \n3. **{answer[2]}** \n4. **{answer[3]}**'
    right_answer = quiz.questions_list[QuestNumber]["right_answer"]

    await channel.send("**Quiz Starting...**")
    time.sleep(1)
    await channel.send(question_content)
    await channel.send(question_answers)
    

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
        await message.channel.send('**Correct answer**')
        nick = str(message.author)
        
        if nick not in quiz_contestants:
            quiz_contestants[nick] = 0
            quiz_contestants[nick] = quiz_contestants[nick]+1

        else:
            quiz_contestants[nick] = quiz_contestants[nick]+1

        newPoints = quiz_contestants[nick]

# Contestants dictionary is also added to contestants.txt file to be used as a backup  

        with open("static/contestants.txt","w") as file:
            file.write(json.dumps(quiz_contestants))

        if newPoints == 1:
            points_message = f'Now **{nick}** has **{newPoints} point**.'
        else:
            points_message = f'Now **{nick}** has **{newPoints} points**.'
            
        await message.channel.send(points_message)

    else:
        await message.channel.send(f'Wrong answer, correct answer is **{answer[right_answer-1]}**')
    
# Command brings up a quiz leaderboard

@client.command(name='leaderboard', help='Shows current quiz leaderboard')
async def leaderboard(ctx):
    for key, val in quiz_contestants.items():
        x = (f"{key}  {val}")
        await ctx.send(x)

    print("all if fine!")
    client.run(TOKEN)
    

if __name__ == "__main__":
    print("all if fine!")
    client.run(TOKEN)