import discord
import random
import os
from discord import FFmpegPCMAudio
from gtts import gTTS
from datetime import datetime
from sys import argv
from os import listdir
from os.path import isfile, join
import webcolors
import vege_learn
import functools

TICK_PATH = 'ticks/'
TICK_FILES = [TICK_PATH + f for f in listdir(TICK_PATH) if isfile(join(TICK_PATH, f))]
PREFIX = 'vege '

client = discord.Client()

with open('greetings.txt') as greetings_file:
    GREETINGS = greetings_file.readlines()

commands = []


def command(name, description, show_in_help=True):
    def add_command(function):
        global commands
        commands.append({'function': function, 'name': name, 'description': description, 'show in help': show_in_help})

    return add_command


class PlayItem:
    def __init__(self, file_name, delete_after=False):
        self.filename = file_name
        self.audio_source = FFmpegPCMAudio(file_name)
        self.delete_after = delete_after


vc = None  # TODO: Allow it to enter more than one voice chat for when its being used on more than one server
play_queue = []
playing = False
play_id = 0

deleted_messages = []
edited_messages = []

for user in os.listdir("immitate"):
    vege_learn.Model(user)


@client.event
async def on_ready():
    print('Bot is ready')

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == 'voice-chat':
                await channel.send('OH MY GOD IM SO READY')
                break


def next_in_queue():
    global playing, play_queue

    if vc is None:
        playing = False
        for i in play_queue:
            if i.delete_after is True:
                os.remove(i.file_name)
        play_queue.clear()
        return

    if len(play_queue) == 0:
        playing = False
        return

    play_item = play_queue.pop(0)

    vc.play(play_item.audio_source, after=lambda x: next_in_queue())


def generate_tts(text):
    global playing, play_id

    voice_text = gTTS(text=text, lang='en', slow=False)

    if not os.path.exists('audio'):
        os.mkdir('audio')

    file_name = 'audio/' + str(play_id) + '.wav'

    play_id = (play_id + 1) % 100000

    voice_text.save(file_name)

    play_queue.append(PlayItem(file_name, delete_after=True))

    if not playing:
        playing = True
        next_in_queue()


@command('say', 'When the bot is in a voice channel it will use text to speech to read your message aloud')
async def say_command(message, args):
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
    elif len(args) == 0:
        await message.channel.send('You need to give me something to say. E.g "vege say fuck you"')
    else:
        generate_tts(args)


@command('come here', 'Will make the bot join the voice channel you are in')
async def join_vc_command(message, args):
    global vc

    voice_state = message.author.voice

    if voice_state is None:
        await message.channel.send('You must be in a voice channel to send this.')
        return

    voice_channel = voice_state.channel

    if voice_channel is None:
        await message.channel.send('You must be in a voice channel to send this.')
        return
    elif vc == voice_channel:
        await message.channel.send('I\'m already in the voice channel')
        return

    vc = await voice_channel.connect()


@command('go away', 'Makes the bot leave the voice channel')
async def leave_vc_command(message, args):
    global vc
    if vc is None:
        return

    await vc.disconnect()
    vc = None


@command('delete history', 'Shows all the messages that have been deleted in this channel in the last 15 minutes')
async def show_delete_history_command(message, args):
    global deleted_messages
    deleted_messages = [m for m in deleted_messages if (datetime.utcnow() - m.created_at).seconds < 15 * 60]

    if len(deleted_messages) == 0:
        await message.channel.send('No messages have been deleted in the last 15 minutes')
        return

    for deleted_message in deleted_messages:
        if deleted_message.channel != message.channel:
            continue

        files = []
        file_urls = []

        for attachment in deleted_message.attachments:
            try:
                files.append(await attachment.to_file(use_cached=True))
            except discord.errors.NotFound:
                file_urls.append(attachment.url)

        response = '{author}, deleted:\n {content}\n{file_urls}'
        response = response.format(
            author=deleted_message.author.mention,
            content=deleted_message.content,
            file_urls='\n'.join(file_urls)
        )
        await message.channel.send(response, files=files)


@command('edit history', 'Shows all the messages that have been edited in this channel in the last 15 minutes')
async def show_edit_history_command(message, args):
    global edited_messages
    edited_messages = [m for m in edited_messages if (datetime.utcnow() - m.created_at).seconds < 15 * 60]

    if len(edited_messages) == 0:
        await message.channel.send('No messages have been edited in the last 15 minutes')
        return

    for edited_message in edited_messages:
        files = []
        file_urls = []

        for attachment in edited_message.attachments:
            try:
                files.append(await attachment.to_file(use_cached=True))
            except discord.errors.NotFound:
                file_urls.append(attachment.url)

        response = '{author}, deleted:\n {content}\n{file_urls}'
        response = response.format(
            author=edited_message.author.mention,
            content=edited_message.content,
            file_urls='\n'.join(file_urls)
        )
        await message.channel.send(response, files=files)


@command('colour me',
         'Colours your name the requested colour. You can give the colour in hex, RGB values or the name of the colour you want')
async def colour_command(message, args):
    if len(args) == 0:
        await message.channel.send('Please give me a colour. E.g. "vege colour me blue"')
        return

    if args.lower() in webcolors.CSS3_NAMES_TO_HEX:
        hex_colour = webcolors.name_to_hex(args)
    elif webcolors.HEX_COLOR_RE.match(args):
        hex_colour = webcolors.normalize_hex(args)
    else:
        try:
            hex_colour = webcolors.rgb_to_hex(map(int, args.replace(',', ' ').split()))
        except ValueError or TypeError:
            await message.channel.send('That is not a valid colour. E.g. "vege colour me blue"')
            return

    discord_color = discord.Color(int(hex_colour[1:], 16))

    role_name = "colour-{}".format(message.author.id)

    if role_name not in [i.name for i in message.guild.roles]:
        role = await message.guild.create_role(name=role_name)
        await message.author.add_roles(role)
    else:
        role = discord.utils.get(message.guild.roles, name=role_name)
    await role.edit(colour=discord_color)
    await message.channel.send('Done')


@command('help', 'Shows you a list of all the commands you can use and a description of how to use them')
async def help_command(message, args):
    response = 'These are all the commands you can use: \n```'
    for i in commands:
        if i['show in help']:
            response += 'vege {name:<20}{description}\n'.format(**i)
    response += '```'
    await message.channel.send(response)


@command('tick', 'Plays a random Min tick', show_in_help=False)
async def tick_command(message, args):
    global playing
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
        return

    play_queue.append(PlayItem(random.choice(TICK_FILES)))

    if not playing:
        playing = True
        next_in_queue()


@command('test greeting', 'Greets the person who writes this in discord', show_in_help=False)
async def test_greeting_command(message, args):
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
    else:
        generate_tts(random.choice(GREETINGS).format(name=message.author.display_name))


@command('immitate', 'Immitates a particular person on the server using machine learning', show_in_help=True)
async def immitate_command(message, args):
    user = args.lower()

    # immitate the person named args
    if vege_learn.has_user(user):
        await message.channel.send(vege_learn.immitate_user(user))


@client.event
async def on_message(message):
    text = message.content.lower()
    if not text.startswith(PREFIX):
        return
    text = text[len(PREFIX):]

    for i in commands:
        if text.startswith(i['name'] + ' ') or text == i['name']:
            await i['function'](message, message.content[len(PREFIX) + len(i['name']) + 1:])  # +1 for space
            break
    else:
        await message.channel.send('That is not a command')


@client.event
async def on_voice_state_update(member, before, after):
    global vc, playing

    if after is not None and vc is not None:
        if before.channel != after.channel and after.channel == vc.channel:
            greeting = random.choice(GREETINGS)
            generate_tts(greeting.format(name=member.display_name))


@client.event
async def on_message_delete(message):
    if message.author.id == client.user.id:
        return

    deleted_messages.append(message)


@client.event
async def on_message_edit(before, after):
    edited_messages.append(before)


# Read bot token
with open(argv[1] if len(argv) > 1 else 'token.txt') as token_file:
    client.run(token_file.read())
