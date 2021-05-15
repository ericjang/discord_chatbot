NLP Games

```
python3.8 bot.py
```

TODO:
    


## Partial Human
  Two players take turn guessing which player's messages are from bot. First player to 5 points wins.
  Status: Mostly implemented, but playtest has a degenerate case where humans end up trying to feint
    the other player into thinking human messages are bot. Bot messages are not realistic enough.

## Role Play and a Bot
  A Jackbox-style word game where people write down prompts for two people to talk about (e.g. couples therapy). In second phase, people go off and have conversations with a partner for 10-20 messages. 

  In third phase, everyone sees all the conversations and guess which players are bots. You get 100
  points for each player you correctly identify as a bot.

  The player who has the most number of people guessing them as a bot loses 100 points, so try to be 
  human! 
  
  Data desiderata:
    - people upvote individual messages being good/bad
    - which conversations are voted highly as human or not.
    - 
