"""Implements the Half Human Game object

TODOs:
 - log conversations so we can re-train model on them later.
"""
import collections
from transformers import pipeline
import random
import enum
import inference_server

def get_player_id(message):
  return str(message.channel.id) + '-' + str(message.author.id)
  
class HalfHumanGame(object):
  # Manages conversation between a bot and multiple players

  def __init__(self, bot_prob=1.0):
    self.player_id_to_channel = {}
    self.bot_prob = bot_prob
    self.convo = inference_server.Conversation()
    self.scores = collections.defaultdict(int)
  
  @property
  def num_players(self):
    return len(self.player_id_to_channel)

  def add_player(self, message):
    self.player_id_to_channel[get_player_id(message)] = message.channel

  async def handle_bot_accusation(self, message):
    # reporting a bot.
    player_id = get_player_id(message)
    if player_id != self.convo.last_player and self.convo.last_message_is_bot():
      self.scores[player_id] += 1
    else:
      self.scores[player_id] -= 1
    await message.reply('Your score is now {}'.format(self.scores[player_id]))
 

  async def handle_message(self, message):
    """Handle message coming from one of the players. Forwards human
    or bot message to all recipients, and appends the user query to 
    the other convo contexts (to be lazily evaluated when the human counterparty
    responds.

    This AI *replaces* messages with bot-generated responses based on
    the *previous* conversational context (i.e. not taking into
    account the *real* response provided by the human player).
    
    If the bot sends the message, the real response provided from 
    the sender is never stored into the conversational context for 
    other players.
    """
    player_id = get_player_id(message)

    if message.content.lower() == "!bot":
      await self.handle_bot_accusation(message)
    else:
      # Send messages 
      if self.convo.last_player != player_id and self.convo.chat_history and random.random() < self.bot_prob:
        # In the future, we can have the bot fill in a multi-line response but that makes game scoring a bit
        # tricky.
        reply = self.convo.get_substitute_response(player_id)
        is_bot = True
        await message.reply('BOT SENT ' + reply + ' INSTEAD OF YOUR MESSAGE')
      else:
        is_bot = False
        reply = message.content
      self.convo.update(player_id, reply, is_bot) 
      # Distribute message to other users
      for other_player_id, channel in self.player_id_to_channel.items():
        if other_player_id != player_id:
          await channel.send(reply)
    
