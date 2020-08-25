import discord
import random
import os
from discord import FFmpegPCMAudio
from gtts import gTTS
from datetime import timedelta, datetime
from sys import argv


PREFIX = 'vege '

client = discord.Client()

with open('greetings.txt') as greetings_file:
    greetings = greetings_file.readlines()

commands = {}


def command(name):
    def add_command(func):
        commands[name] = func
    return add_command


vc = None

play_queue = []
playing = False
play_id = 0

deleted_messages = []
edited_messages = []


@client.event
async def on_ready():
    print('Bot is ready')

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == 'voice-chat':
                await channel.send('OH MY GOD IM SO READY')
                break


def next_in_queue(error=None, file_name=None):
    global playing, play_queue

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

        for file in os.listdir('audio'):
            os.remove('audio/' + file)

        return

    vc.play(audio_source, after=lambda x: next_in_queue(x, file_name))


def generate_tts(text):
    global playing, play_id

    voice_text = gTTS(text=text, lang='en', slow=False)

    if not os.path.exists('audio'):
        os.mkdir('audio')

    file_name = 'audio/' + str(play_id) + '.wav'

    play_id = (play_id + 1) % 100000

    voice_text.save(file_name)
    play_queue.append(file_name)

    if not playing:
        playing = True
        next_in_queue()


@command('say')
async def say(message, args):
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
    elif len(args) == 0:
        await message.channel.send('You need to give me something to say. E.g "vege say fuck you Tyler"')
    else:
        generate_tts(args)


@command('come here')
async def join_vc(message, args):
    global vc
    voice_state = message.author.voice

    if voice_state is None:
        return

    voice_channel = voice_state.channel

    if voice_channel is None:
        await message.channel.send('You must be in a voice channel to send this.')
        return

    vc = await voice_channel.connect()


@command('go away')
async def leave_vc(message, args):
    global vc
    if vc is None:
        return

    await vc.disconnect()
    vc = None


@command('delete history')
async def show_history(message, args):
    global deleted_messages
    deleted_messages = [m for m in deleted_messages if (datetime.utcnow() - m.created_at).seconds < 15 * 60]

    if len(deleted_messages) == 0:
        await message.channel.send('No messages have been deleted in the last 15 minutes')
        return

    for i in deleted_messages:
        if i.channel != message.channel:
            continue

        await message.channel.send(i.author.mention + ', deleted:\n' + i.content)

        for attachment in i.attachments:
            try:
                file = await attachment.to_file(use_cached=True)

                await message.channel.send(file=file)
            except discord.errors.NotFound:
                print('Could not post deleted image')


@command('edit history')
async def show_history(message, args):
    global edited_messages
    edited_messages = [m for m in edited_messages if (datetime.utcnow() - m.created_at).seconds < 15 * 60]

    if len(edited_messages) == 0:
        await message.channel.send('No messages have been edited in the last 15 minutes')
        return

    for i in edited_messages:
        if i.channel != message.channel:
            continue

        await message.channel.send(i.author.mention + ', edited:\n' + i.content)

        for attachment in i.attachments:
            try:
                file = await attachment.to_file(use_cached=True)

                await message.channel.send(file=file)
            except discord.errors.NotFound:
                print('Could not post deleted image')


@client.event
async def on_message(message):
    text = message.content.lower()
    if not text.startswith(PREFIX):
        return
    text = text[len(PREFIX):]

    for name, func in commands.items():
        if text.startswith(name):
            await func(message, message.content[len(PREFIX) + len(name) + 1:])  # +1 for space
            break
    else:
        await message.channel.send('That is not a command')


@client.event
async def on_voice_state_update(member, before, after):
    global vc, playing

    if after is not None and vc is not None:
        if before.channel != after.channel and after.channel == vc.channel:
            greeting = random.choice(greetings)
            generate_tts(greeting.format(name=member.display_name))


@client.event
async def on_message_delete(message):
    if message.author.id == 746605769641951313:
        return

    deleted_messages.append(message)


@client.event
async def on_message_edit(before, after):
    edited_messages.append(before)


# Read bot token
with open(argv[1] if len(argv) > 1 else 'token.txt') as token_file:
    client.run(token_file.read())
