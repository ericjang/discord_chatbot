"""Tests for game.py"""
import asyncio
from game import HalfHumanGame
import collections
class MockChannel(object):
  def __init__(self, id):
    self.id = id
    
  async def send(self, text):
    # just prints what the other client receives (but takes no action on)
    print('sending %s' % text)
    pass
    
Author = collections.namedtuple('MockAuthor', ['id'])    

class MockMessage(object):
  def __init__(self, channel, author_id, text):
    self.author = Author(author_id)
    self.content = text
    self.channel = channel
  async def reply(self, text):
    pass

def step(future):
  # blocking execution 
  loop = asyncio.get_event_loop()
  task = loop.create_task(future)
  loop.run_until_complete(task)



def main():
  game = HalfHumanGame(bot_prob=0.5)

  a1, a2 = 123, 234
  c1 = MockChannel(1)
  c2 = MockChannel(2)

  # player 1 start message
  m1 = MockMessage(c1, a1, '!play')
  game.add_player(m1)
  # Player 2 joins
  m2 = MockMessage(c2, a2, '!play')
  game.add_player(m2)

  # Player 1 sends initial message
  m1 = MockMessage(c1, a1, "hello, hows it going")  
  step(game.handle_message(m1))

  # Player 2 replies
  m2 = MockMessage(c2, a2, "not bad, how about yourself")
  step(game.handle_message(m2))
 
  # Player 1 replies again
  m1 = MockMessage(c1, a1, "hows ur week going haha")
  step(game.handle_message(m1))

  # Player 2 replies again
  m2 = MockMessage(c2, a2, "just bored lol")
  step(game.handle_message(m2))

  # Print the two conversations
  print(game.convo)

main()

