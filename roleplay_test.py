"""Tests for game.py"""
import asyncio
import roleplay_and_a_bot
import collections

GameState = roleplay_and_a_bot.GameState

class MockChannel(object):
  def __init__(self, id):
    self.id = id
    
  async def send(self, text):
    # just prints what the other client receives (but takes no action on)
    print('{} received {}'.format(self.id, text))
    
Author = collections.namedtuple('MockAuthor', ['id'])    

class MockMessage(object):
  def __init__(self, channel, author_id, text):
    self.author = Author(author_id)
    self.content = text
    self.channel = channel
  async def reply(self, text):
    print('{} received {} (reply)'.format(self.channel.id, text))

def step(future):
  # blocking execution 
  loop = asyncio.get_event_loop()
  task = loop.create_task(future)
  loop.run_until_complete(task)



async def main():
  # convo session lasts 5 seconds.
  game = roleplay_and_a_bot.RolePlayGame(convo_timeout=10., nobot_mode=True)

  ROOM_CODE='7x3k'

  N = 4
  # Create 3 players and join a game
  author_ids = list(range(1, N+1))
  channel_ids = author_ids
  channels = []
  for aid, cid in zip(author_ids, channel_ids):
    c = MockChannel(cid)
    channels.append(c)
    m = MockMessage(c, aid, '!play {}'.format(ROOM_CODE))
    await game.add_player(m)

  assert game.num_players == N
  assert game.state == GameState.WAITING

  # Player 1 starts the game
  m = MockMessage(channel_ids[0], author_ids[0], '!start')
  await game.handle_message(m)

  # check that each player is given a prompt
  assert game.state == GameState.PROMPT 

  # send prompts for each player
  for aid, c in zip(author_ids, channels):
    m = MockMessage(c, aid, "Prompt from %s (A) (B)" % aid)
    await game.handle_message(m)

  # Make sure all authors have submitted prompts.
  # at this point, players should get paired up
  assert game.num_prompts == len(author_ids)
  assert game.state == GameState.CONVO
  
  # Each player sends a message
  for aid, c in zip(author_ids, channels):
    m = MockMessage(c, aid, "hullo")
    await game.handle_message(m)

  # Wait for convos to finish up
  await asyncio.sleep(game.convo_timeout + 1)

  assert game.state == GameState.JUDGE

  # Everyone votes player 1 as the bot / player missing context
  for i, (aid, c) in enumerate(zip(author_ids, channels)):
    m = MockMessage(c, aid, str(i+1))
    await game.handle_message(m)

  assert game.state == GameState.WAITING

asyncio.run(main())

