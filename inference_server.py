import asyncio
import random
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Optional

def get_player_id(m):
  return str(m.channel.id) + '-' + str(m.author.id)


class Conversation(object):
  """Manages encoded history for multiplayer conversation.
  One of the players may be a bot.
  """

  def __init__(self, prompt=""):
    self.tokenizer = None
    self.model = None
    self.model_id = None
    self.prompt = prompt
    # player may be a bot
    self.role_to_player = {}
    self.chat_history = [] # plaintext representation.
    self.last_role = None
    self.bot_role = None # Denotes which role is the bot

  def add_player(self, player, role):
    self.role_to_player[role] = player
    player.role = role
    player.convo = self
    if player.bot:
      self.bot_role = role
      self.model_id = "microsoft/DialoGPT-large"
      model = self.model_id
      print('Loading Model %s' % model) 
      # In the future, a shared inference server serves all requests
      self.tokenizer = AutoTokenizer.from_pretrained(model)
      self.model = AutoModelForCausalLM.from_pretrained(model)
    
  async def handle_convo(self, role, content):
    self.update(role, content, bot=role == self.bot_role)
    # forward to all other players
    sender = self.role_to_player[role]
    tasks = []
    for alt_role, alt_player in self.role_to_player.items():
      if alt_role != role:
        if alt_player.bot:
          # TODO: schedule async background task for bot to reply.
          # Note that bot might respond to itself!
          # this is not added to tasks - bot responds whenever.
          asyncio.create_task(self.bot_respond())
        else:
          tasks.append(asyncio.create_task(
              alt_player.channel.send("{}>> {}".format(role, content))))
    if tasks:
      await asyncio.wait(tasks)

  def update(self, role: str, next_input: str, bot: bool):
    self.chat_history.append((role, next_input, bot))
    self.last_role = role

  def last_message_is_bot(self):
    return self.chat_history and self.chat_history[-1][2]

  async def maybe_bot_initiate(self):
    await asyncio.sleep(3)
    # by the time we get here, user might have sent a message.
    # only send message if other user hasn't sent yet
    if self.last_role is None:
      asyncio.create_task(self.bot_respond())
    
  def get_chat_history(self):
    curr_role = None
    # Prepend the context
    chat_history = ""
    chat_history += self.prompt + self.tokenizer.eos_token
    for r, t, b in self.chat_history:
      if curr_role is None:
        curr_role = r
      elif r != curr_role:
        # speaker has switched, terminate past speaker sentence.
        chat_history += self.tokenizer.eos_token
      chat_history += t
    # Either the bot continues its own writing, or it finishes user response
    # self.last_role might be None if bot is speaking first.
    if self.last_role and not self.role_to_player[self.last_role].bot:
      # Terminate with eos token so model knows to respond.
      chat_history += self.tokenizer.eos_token
    return chat_history

  async def bot_respond(self):
    # wait a number of seconds, then respond.
    sleep_delay = random.choice([1, 2])
    print('sleeping for %d seconds' % sleep_delay)
    await asyncio.sleep(sleep_delay)

    chat_history = self.get_chat_history()
    chat_history_ids = self.tokenizer.encode(chat_history, return_tensors='pt')
    # predict
    output_history_ids = self.model.generate(chat_history_ids, max_length=1000,
      do_sample=True, pad_token_id=self.tokenizer.eos_token_id)
    response_ids = output_history_ids[:, chat_history_ids.shape[-1]:][0]
    # Decode
    response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
    # Which bot responds? If last_role is a bot, use last_role to continue
    # its train of thought. Otherwise, find the first player that is a bot
    # and have them respond.
    await self.handle_convo(self.bot_role, response)

  def __repr__(self):
    s = ""
    for p, t, b in self.chat_history:
      s += "{} (bot={}): {}\n".format(p,b, t)
    return s   


if __name__ == "__main__":
  c = Conversation()
  players = ["A", "B"]
  c.update("B", "hi, how's it going?")
  for i in range(5):
    p = players[i % 2]
    r = c.get_substitute_response(p)
    c.update(p, r)
