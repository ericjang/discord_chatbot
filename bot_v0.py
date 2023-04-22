"""
TODO:
- !play - detect if there are more than two people in the channel. 
"""
from game import HalfHumanGame, get_player_id


import discord
TOKEN='YOUR_TOKEN_HERE'

GAME_START="""

You've been matched with a bot and a real human player, named "J". 

Your mission is to figure out when messages are sent by the bot, and
when messages are sent by the human. 

Sometimes J's replys are coming from a human, so messages may not arrive right away
Type !help for how to play the game.
"""

HELP="""
PARTIAL HUMAN: HOW TO PLAY

!help
  Displays this help message

!play
  You converse with J. Some of the time, J's messages come from a human.
  Some of the time, J's messages come from a bot. Reply to their
  messages with !bot. If you guess right, you get 1 point.
  If you guess wrong, you lose one point. If you don't guess, you get 0 points.
  If your human counterparty receives a bot message instead of yours, you will
  see what their bot told them instead of your message. The first human player 
  to get 30 points wins (and then the game ends).

!end
  Ends the game and unmatches you with the current human player. This will
  also end the other human player's session.

!bot
  Declare J's last message to be coming from the bot.

!report
  Report your counterparty (human or bot) for an inappropriate message.
  The conversation will be reviewed by a human.
"""

RULES="""
What's my current score?
  Score is not shown until one player has won the game. You can check your
  account balance at any time via `!balance`

What am I allowed to talk about?
  You can talk about almost anything, but do not share personally identifiable information 
  like name, address, online account usernames, etc. Your messages may be 
  used to further train and improve the AI to imitate realistic human conversation. Violating
  these rules will be met with account bans.

"""
ACCOUNT_BALANCE = """

Account Balance: 0.05 ETH
Num Wins: 45
Num Losses: 10
"""




TEXT_COMMANDS=["!help", "!rules", "!balance"]
TEXT_REPLIES=[HELP, RULES, ACCOUNT_BALANCE]
TEXT_CMD_MAP = dict(zip(TEXT_COMMANDS, TEXT_REPLIES))

class MyClient(discord.Client):

    def __init__(self, **kwargs):
        super(MyClient, self).__init__(**kwargs)
        # A List of HalfHuman Games being hosted by this bot, some of which
        # contain unmatched players.
        self.games = []
        self.player_id_to_game = {}
        
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    def get_game(self, player_id):
        # get the game session for the player
        return self.player_id_to_game[player_id]
    
    def join_or_start_game(self, message):
        # find an available game to join or create a new one
        player_id = get_player_id(message)
        print(player_id)
        print('%d existing games' % len(self.games))
        match = False
        for g in self.games:
            if g.num_players == 1:
                print('joining existing game') 
                g.add_player(message)
                match = True
                self.player_id_to_game[player_id] = g
                break
        if not match:
            print('No unmatched game sessions, starting a new one.')
            g = HalfHumanGame(bot_prob=0.5)
            g.add_player(message)
            self.player_id_to_game[player_id] = g
            self.games.append(g)
        
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        channel = message.channel
        player_id = get_player_id(message)
        if message.content == "!play":
            await channel.send(GAME_START)
            self.join_or_start_game(message)
        elif message.content in TEXT_COMMANDS:
            await channel.send(TEXT_CMD_MAP[message.content])
        elif player_id in self.player_id_to_game:
          # Save the message object
          game = self.get_game(player_id)
          if game.num_players < 2:
            await channel.send('Game needs two or more players to start.')
          else:
            # Game object sends things to both players.
            await game.handle_message(message)
        else:
          if player_id not in self.player_id_to_games:
            await channel.send('Player not joined. Please join a game to start playing.')
          print('no matching handler event')

client = MyClient()
client.run(TOKEN)

