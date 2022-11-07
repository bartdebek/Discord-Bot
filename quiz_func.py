import random
import json



class Quiz:

    f = open("static/questionList.json") 
    questions_list = json.load(f)
    questions_list = questions_list["trivia_questions"]

    def question_draw(self):
        """
        Function that draws a quiz question number 
        to be asked when used with !quiz command
        """
        self.question_number = random.randint(0,len(self.questions_list)-1)
        return self.question_number


    # # Assign Discord token kept in .env file

    # load_dotenv()
    # TOKEN = os.getenv('DISCORD_TOKEN') 

    # # Open a file with quiz questions


        
    # # Assign "!" as a prefix to Discord commands
    # client = commands.Bot(command_prefix='!')

    # # Commands to send a random quote from Confucius

    # @client.command(name='konf', help='Displays a random quote from Confucius')
    # async def janusz(ctx):
    #     cytaty_korwina = mylist

    #     response = random.choice(cytaty_korwina)
    #     await ctx.send(response)


    # # Commands to send a random question to the person that send "!quiz" message.

    # @client.command(name='quiz', help='Shows a general knowledge question. You can receive points for guessing correctly!')
    # async def on_message(message):
    #     channel = message.channel

    # # Drawing and sending the question as a discord message

    #     QuestNumber = Bot.question_draw()
    #     answer = questions_list[QuestNumber]["answers"]
    #     await channel.send("Quiz Starting...")
    #     await channel.send(questions_list[QuestNumber]["question"])
    #     await channel.send(f'1. {answer[0]} \n2. {answer[1]} \n3. {answer[2]} \n4. {answer[3]}')
    #     rightAnswer = questions_list[QuestNumber]["right_answer"]

    # # Checking if author of answer was the person who used "!quiz" command, 
    # # setting the maximum annswer time to 60 seconds. 

    #     def check(m):
    #         return m.author == message.author
    #     try:
    #         guess = await client.wait_for('message', check=check , timeout=60.0)
    #     except asyncio.TimeoutError:
    #         await message.channel.send('Time is up')

    # # If answer is given, program checks if it is the same as correct answer, if yes points are awarded accordingly. 

    #     if int(guess.content) == rightAnswer:
    #         await message.channel.send('Correct answer')
    #         nick = str(message.author)
            
    #         if nick not in quizContestants:

    #             quizContestants[nick] = 0
    #             quizContestants[nick] = quizContestants[nick]+1

    #         else:

    #             quizContestants[nick] = quizContestants[nick]+1

    #         newPoints = quizContestants[nick]

    # # Contestants dictionary is also added to contestants.txt file to be used as a backup  

    #         with open("contestants.txt","w") as file:
    #             file.write(json.dumps(quizContestants))
    #         pointsMessage = (f'Now {nick} has {newPoints} points.')
    #         await message.channel.send(pointsMessage)

    #     else:
    #         await message.channel.send(f'Wrong answer, correct answer is {answer[rightAnswer-1]}')
    #         print(rightAnswer)
        
    # # Command brings up a quiz leaderboard

    # @client.command(name='leaderboard', help='Shows current quiz leaderboard')
    # async def leaderboard(ctx):
    #     for key, val in quizContestants.items():
    #         x = (f"{key}  {val}")
    #         await ctx.send(x)

