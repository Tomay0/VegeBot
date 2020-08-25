import discord
import random
import os
from discord import FFmpegPCMAudio
from gtts import gTTS

from datetime import timedelta, datetime

client = discord.Client()

with open("greetings.txt", "r") as greetings_file:
    greetings = greetings_file.readlines()

vc = None

play_queue = []
playing = False
play_id = 0

deleted_messages = []
edited_messages = []


@client.event
async def on_ready():
    print("Bot is ready")

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == "voice-chat":
                await channel.send("OH MY GOD IM SO READY")
                break


def next_in_queue(error=None, file_name=None):
    global playing, play_queue

    print("Finished playing")

    if file_name is not None:
        os.remove(file_name)

    if len(play_queue) == 0:
        playing = False
        return

    file_name = play_queue.pop(0)
    audio_source = FFmpegPCMAudio(file_name)

    if vc is None:
        playing = False
        play_queue.clear()

        for file in os.listdir("audio"):
            os.remove("audio/" + file)

        return

    vc.play(audio_source, after=lambda x: next_in_queue(x, file_name))


def say(text):
    global playing, play_id

    voice_text = gTTS(text=text, lang='en', slow=False)

    if not os.path.exists("audio"):
        os.mkdir("audio")

    file_name = "audio/" + str(play_id) + ".wav"

    play_id = (play_id + 1) % 100000

    voice_text.save(file_name)
    play_queue.append(file_name)

    if not playing:
        playing = True
        next_in_queue()


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
