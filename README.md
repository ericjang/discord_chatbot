NLP Games

Implementation of some simple Discord-based text games. I hacked this together in a weekend in 2021, the code is kind of shit.

## General Challenge with Detect-the-Bot Style Games

One hopes that having a human generator-discriminator game for bot vs. human generated text would create interesting human-like data. However, the conversations often devolve into people trying to "prompt inject" one another to saying something bot-like, or behaving like a bot themselves. In other words, this game minimizes the divergence between the humans and bots, but in the wrong way (the humans learn to match the bots rather than the other way around). I am not sure if improving the dialogue agent (e.g. GPT-4) would substantially alter these dynamics.

## Role Play and a Bot

Discord bot: `bot.py`

A multiplayer word game where people write down prompts for two people to talk about (e.g. couples therapy). In second phase, people go off and have conversations with a partner for 10-20 messages. 

if `nobot=True`, then this plays in a mode where one player is "Clueless" and does not have the context of the conversation. This is similar to a party game like Jackbox, and can generate useful data for training bots that have to rapidly figure out what the topic is.

If `nobot=False`, then this plays in a mode where one player is a bot simulated via a language model.

In third phase, everyone sees all the conversations and guess which players are bots / clueless. You get 100
points for each player you correctly identify as a bot. The player who has the most number of people guessing them as a bot loses 100 points, so try to be 
human! 

## Partial Human

Discord bot: `bot_v0.py`

Two players take turn guessing which player's messages are from bot. First player to 5 points wins.
Status: Mostly implemented, but playtest has a degenerate case where humans end up trying to feint the other player into thinking human messages are bot. Bot messages are not realistic enough.
