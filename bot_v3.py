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
    help="Shows a general knowledge question. You can receive points for guessing correctly!",
)
async def on_message(ctx):
    """Draw a random question and present it as a button-based quiz.

    A ``QuizView`` (created from JSON) supplies clickable answer buttons
    and automatically handles checking the response and awarding points.
    """

    quiz = Quiz()
    await ctx.send("**Quiz Starting...**")
    await asyncio.sleep(1)

    from utils import QuizView
    view = QuizView(quiz, author=ctx.author)
    embed = view.embed or discord.Embed(description=quiz.question_content)
    await ctx.send(embed=embed, view=view)


@client.command(name="leaderboard", help="Shows current quiz leaderboard")
async def leaderboard(ctx):
    """
    Function to bring up a quiz leaderboard, results are sorted from highest to lowest.

    We reload the contestants from disk before printing so that if any
    code has updated the storage file outside of the in-memory list
    (or if we accidentally have stale objects) we still show the latest
    values.
    """
    global quiz_contestants
    quiz_contestants = Player.load_all()
    for player in sorted(quiz_contestants, key=lambda x: x.points, reverse=True):
        player_stats = f"{player.name}  {player.points}"
        await ctx.send(player_stats)

@client.command(name="stats", help="Shows your quiz stats")
async def stats(ctx):
    """
    Function to show quiz stats of a player, including points, correct and wrong answers.

    Reload players first to keep the view aligned with the file.
    """
    global quiz_contestants
    quiz_contestants = Player.load_all()

    nick = str(ctx.author)
    for player in quiz_contestants:
        if player.name == nick:
            await ctx.send(str(player))
            break


if __name__ == "__main__":
    client.run(TOKEN)
