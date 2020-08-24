import discord
import random
from discord import FFmpegPCMAudio
import pyttsx3

from datetime import timedelta, datetime

client = discord.Client()

greetings = [
    "Watch out everyone it is {name}",
    "Hello, {name}",
    "Lol fuck off {name}",
    "Party's over, {name} has joined",
    "Hi, {name}. I love you",
    "Ayyy it's {name}, hello",
    "Hoodle",
    "Welcome to voice chat, {name}",
    "I was having a great day until {name} joined",
    "Hi Tyler. Oh sorry, I mean {name}",
    "Who just joined? Oh it's {name}",
    "A cutie named {name} just joined",
    "I hope everyone has a good day except {name}",
    "{name} is looking like an art hoe today",
    "Everyone give {name} a vibe check",
    "Everyone move to the other channel, {name} has joined",
    "Oh no, everyone mute {name}",
    "Everyone kink shame {name}",
    "Sad peepos in the chat, {name} is here",
    "Somone call The Undateables, {name} is here",
    "Somone call Bum Fights, {name} is here",
    "speaking of unfuckable, {name} is here",
    "fuck me sideways and call me {name}",
    "Oh no, look who decided to show up. It's {name}",
    "Time to open up the Cum Zone, {name} is here",
    "dicks out for {name}",
    "Wussup {name}",
    "How to mute {name} on discord. Wait this isn't google",
    "Police? Yep. {name} is here. We'll keep them occupied",
    "hide your children its {name}",
    "Oh hi {name}, we were just shit-talking you"
]


text_channels = []
voice_channels = []

vc = None
tts_engine = pyttsx3.init()

play_queue = []
playing = False

deleted_messages = []
edited_messages = []


@client.event
async def on_ready():
    print("Bot is ready")

    for guild in client.guilds:
        for channel in guild.text_channels:
            text_channels.append(channel)
        for channel in guild.voice_channels:
            voice_channels.append(channel)

    for channel in text_channels:
        # TODO make this configurable
        if channel.name == "voice-chat":
            await channel.send("OH MY GOD IM SO READY")


def next_in_queue(error):
    global playing, play_queue

    if len(play_queue) == 0:
        playing = False
        return

    text = play_queue.pop(0)

    tts_engine.save_to_file(text, 'vege.wav')
    tts_engine.runAndWait()

    audio_source = FFmpegPCMAudio('vege.wav')

    if vc is None:
        playing = False
        play_queue.clear()
        return

    vc.play(audio_source, after=next_in_queue)


def say(text):
    global playing

    play_queue.append(text)

    if not playing:
        playing = True
        next_in_queue(None)


@client.event
async def on_voice_state_update(member, before, after):
    global vc, playing

    if after is not None and vc is not None:
        if before.channel != after.channel and after.channel == vc.channel:
            greeting = random.choice(greetings)
            say(greeting.format(name=member.display_name))


@client.event
async def on_message(message):
    global vc, playing
    if message.content.lower() == "vege go away":
        if vc is not None:
            await vc.disconnect()
            vc = None
    elif message.content.lower() == "vege come here":
        voice_state = message.author.voice

        if voice_state is not None:
            voice_channel = voice_state.channel

            if voice_channel is not None:
                vc = await voice_channel.connect()
            else:
                await message.channel.send("You must be in a voice channel to send this.")
    elif message.content.lower().startswith("vege say "):
        if vc is not None:
            text = message.content[9:]

            say(text)
        else:
            await message.channel.send("I'm not in a voice channel. Join a voice channel and type \"vege come here\"")
    elif message.content.lower() == "vege delete history":
        filter(lambda x: (x.created_at - datetime.now()).minutes < 15, deleted_messages)
        for i in deleted_messages:
            if i.channel != message.channel:
                continue

            await message.channel.send(i.author.mention + ", deleted:\n" + i.content)

            for attachment in i.attachments:
                try:
                    file = await attachment.to_file(use_cached=True)

                    await message.channel.send(file=file)
                except discord.errors.NotFound:
                    print("Could not post deleted image")
    elif message.content.lower() == "vege edit history":
        filter(lambda x: (x.created_at - datetime.now()).minutes < 15, edited_messages)
        for i in edited_messages:
            if i.channel != message.channel:
                continue

            await message.channel.send(i.author.mention + ", edited:\n" + i.content)

            for attachment in i.attachments:
                try:
                    file = await attachment.to_file(use_cached=True)

                    await message.channel.send(file=file)
                except discord.errors.NotFound:
                    print("Could not post image")
    elif message.content.lower().startswith("vege "):
        await message.channel.send("That is not a command")
    elif message.content.lower().startswith("vegy "):
        await message.channel.send("My name is vege not vegy you stupid fuck")


@client.event
async def on_message_delete(message):
    if message.author.id == 746605769641951313:
        return

    deleted_messages.append(message)


@client.event
async def on_message_edit(before, after):
    edited_messages.append(before)


# Read bot token
# Create a token.txt with your own token if you want to use this bot

with open("token.txt", "r") as token_file:
    client.run(token_file.read())
