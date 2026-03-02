import os
import random
import time
import json
import asyncio
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import Quiz, Player

# Open a xls file with quotes and ads them to the list that is used by a bot
df = pd.read_excel("static/cytaty.xls")
mylist = df["Listacytatow"].tolist()


# List of Player objects that participate in the quiz.  Load from
# disk using the new convenience method; we no longer keep raw dicts in
# memory.
quiz_contestants = Player.load_all()


def get_player(nick: str) -> Player:
    """Return existing Player with that name or create a new one.

    The new instance is appended to ``quiz_contestants`` so it will
    eventually be persisted by ``Player.save`` calls triggered by
    mutate methods.
    """
    for p in quiz_contestants:
        if p.name == nick:
            return p
    new = Player(nick)
    quiz_contestants.append(new)
    return new

# Assign Discord token kept in .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Assign "!" as a prefix to Discord commands
client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@client.command(name="konf", help="Displays a random quote from Confucius")
async def conf(ctx):
    """
    Function sends random Confucius quote
    """
    confucius_quote = mylist
    response = random.choice(confucius_quote)
    await ctx.send(response)


@client.command(
    name="quiz",
    help="Shows a general knowledge question."
    "You can receive points for guessing correctly!",
)
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
        guess = await client.wait_for("message", check=check, timeout=60.0)
    except asyncio.TimeoutError:
        await message.channel.send("Time is up")

    """
    If answer is given, program checks if it is the same as correct answer, if yes points are awarded accordingly.
    """
    if int(guess.content) == quiz.right_answer:
        await message.channel.send("**Correct answer**")
        nick = str(message.author)
        player = get_player(nick)
        player.add_points()

        # still update the plain-text backup if you like;
        # this is optional now that persistence lives in Player.save().
        with open("static/contestants.json", "w", encoding="utf-8") as file:
            file.write(json.dumps([p.to_dict() for p in quiz_contestants]))
        if player.points == 1:
            points_message = f"Now **{nick}** has **{player.points} point**."
        else:
            points_message = f"Now **{nick}** has **{player.points} points**."

        await message.channel.send(points_message)

    else:
        nick = str(message.author)
        player = get_player(nick)
        player.add_wrong_answer()
        await message.channel.send(
            f"Wrong answer, correct answer is **{quiz.answer[quiz.right_answer-1]}**"
        )


@client.command(name="leaderboard", help="Shows current quiz leaderboard")
async def leaderboard(ctx):
    """
    Function to bring up a quiz leaderboard, results are sorted from highest to lowest
    """
    for player in sorted(quiz_contestants, key=lambda x: x.points, reverse=True):
        player_stats = f"{player.name}  {player.points}"
        await ctx.send(player_stats)

@client.command(name="stats", help="Shows your quiz stats")
async def stats(ctx):
    """
    Function to show quiz stats of a player, including points, correct and wrong answers
    """
    nick = str(ctx.author)
    for player in quiz_contestants:
        if player.name == nick:
            await ctx.send(str(player))
            break


if __name__ == "__main__":
    client.run(TOKEN)
