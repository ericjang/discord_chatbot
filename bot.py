import roleplay_and_a_bot
import discord
TOKEN='YOUR_TOKEN_HERE'

get_player_id = roleplay_and_a_bot.get_player_id

TEXT_COMMANDS=["!help"]
TEXT_REPLIES=[roleplay_and_a_bot.GAME_RULES]
TEXT_CMD_MAP = dict(zip(TEXT_COMMANDS, TEXT_REPLIES))

class MyClient(discord.Client):

    def __init__(self, **kwargs):
        super(MyClient, self).__init__(**kwargs)
        # A List of HalfHuman Games being hosted by this bot, some of which
        # contain unmatched players.
        self.games = {}
        self.player_id_to_game = {}
        
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    def get_game(self, player_id):
        # get the game session for the player
        return self.player_id_to_game[player_id]
    
    async def join_or_start_game(self, room_code, message):
        # find an available game to join or create a new one
        player_id = get_player_id(message)
        if room_code in self.games:
            g = self.games[room_code]
        else:
            print("Creating room.")
            g = roleplay_and_a_bot.RolePlayGame(nobot_mode=True)
            self.games[room_code] = g 
        await g.add_player(message)
        self.player_id_to_game[player_id] = g
        
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        channel = message.channel
        player_id = get_player_id(message)
        if "!play" in message.content:
            tokns = message.content.split(" ")
            if len(tokns) != 2:
                await channel.send("Invalid room code. To join a game room, type `!play <ROOM_CODE>`.")
            else:
                room_code = tokns[1]
                await self.join_or_start_game(room_code, message)
        elif message.content in TEXT_COMMANDS:
            await channel.send(TEXT_CMD_MAP[message.content])
        elif player_id in self.player_id_to_game:
          # Save the message object
          game = self.get_game(player_id)
          # Game object sends things to both players.
          await game.handle_message(message)
        else:
          # if player_id not in self.player_id_to_game:
          #   await channel.send('Player not joined. Please join a game to start playing.')
          print('no matching handler event')

client = MyClient()
client.run(TOKEN)

