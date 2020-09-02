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
import tweepy
from commands import *

from asgiref.sync import async_to_sync

TICK_PATH = 'ticks/'
TICK_FILES = [TICK_PATH + f for f in listdir(TICK_PATH) if isfile(join(TICK_PATH, f))]

# Greetings
if os.path.exists('greetings.txt'):
    with open('greetings.txt') as greetings_file:
        GREETINGS = greetings_file.readlines()

client = discord.Client()
cs = CommandSystem('vege ', client)

vc = None
play_queue = []
playing = False
play_id = 0

with open('channel-name.txt', 'r') as file:
    bot_channel_name = file.read()
bot_channel = None

deleted_messages = []
edited_messages = []


# load neural network models
if os.path.exists('imitate'):
    for user in os.listdir('imitate'):
        vege_learn.Model(user)


@async_to_sync
async def send_channel_message(message):
    print("sending message: " + message)
    if bot_channel is not None:
        await bot_channel.send(message)


# listens to twitter tweets
class TwitterListener(tweepy.StreamListener):
    def on_status(self, status):
        if 'retweeted_status' not in status._json:
            send_channel_message(status.text)


# Twitter API
if os.path.exists('twitter_tokens.txt') and os.path.exists('following.txt'):
    with open('twitter_tokens.txt', 'r') as twitter_tokens:
        TOKENS = twitter_tokens.readlines()

        auth = tweepy.OAuthHandler(TOKENS[0].strip(), TOKENS[1].strip())
        auth.set_access_token(TOKENS[2].strip(), TOKENS[3].strip())

        api = tweepy.API(auth)
        streamListener = TwitterListener()
        stream = tweepy.Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')

        following = []
        with open('following.txt', 'r') as following_file:
            for line in following_file:
                following.append(line.strip())

        try:
            stream.filter(follow=following, is_async=True)
        except:
            send_channel_message("OOF. I think I just lost connection to twitter.")
            stream.disconnect()
else:
    print("Could not find twitter_tokens.txt. You cannot use the ")


class PlayItem:
    def __init__(self, file_name, delete_after=False):
        self.filename = file_name
        self.audio_source = FFmpegPCMAudio(file_name)
        self.delete_after = delete_after


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


@cs.add_command('say', 'Will say out loud any text you give it', arguments=AnyText())
async def say_command(message, args):
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
    elif len(args) > 300:
        await message.channel.send('I can\'t say that, it\'s to long')
    else:
        generate_tts(args)


@cs.add_command(
    'come here',
    'Will make the bot join the voice channel you are in',
    aliases=['come', 'join']
)
async def join_vc_command(message, args):
    global vc

    voice_state = message.author.voice

    if voice_state is None:
        await message.channel.send('You must be in a voice channel to send this.')
        return

    if vc is not None and vc.channel == voice_state.channel:
        await message.channel.send('I\'m already in the voice channel')
        return

    if vc is not None:  # In another VC
        await vc.disconnect()

    vc = await voice_state.channel.connect()


@cs.add_command(
    'go away',
    'Makes the bot leave the voice channel',
    aliases=['go', 'leave', 'fuck off']
)
async def leave_vc_command(message, args):
    global vc
    if vc is None:
        return

    await vc.disconnect()
    vc = None


@cs.add_command(
    'delete history',
    'Shows all the messages that have been deleted in this channel in the last 15 minutes'
)
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


@cs.add_command(
    'edit history',
    'Shows all the messages that have been edited in this channel in the last 15 minutes'
)
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


@cs.add_command(
    'colour me',
    'Will change the color of your discord name whatever you request',
    aliases=['color me', 'colour', 'color'],
    arguments=Or(ColorHex(), CSS3Name(), RGBValues())
)
async def colour_command(message, args):
    if args.lower() in webcolors.CSS3_NAMES_TO_HEX:
        hex_colour = webcolors.name_to_hex(args)
    elif webcolors.HEX_COLOR_RE.match(args):
        hex_colour = webcolors.normalize_hex(args)
    else:
        hex_colour = webcolors.rgb_to_hex(map(int, args.replace(',', ' ').split()))

    # because black is not allowed
    if hex_colour == '#000000':
        hex_colour = '#010101'

    discord_color = discord.Color(int(hex_colour[1:], 16))

    role_name = "colour-{}".format(message.author.id)

    if role_name not in [i.name for i in message.guild.roles]:
        role = await message.guild.create_role(name=role_name)
        await message.author.add_roles(role)
    else:
        role = discord.utils.get(message.guild.roles, name=role_name)
    await role.edit(colour=discord_color)
    await message.channel.send('Done')


@cs.add_command(
    'tick',
    'Plays a random Min tick',
    aliases=['hoodle'],
    show_in_help=False
)
async def tick_command(message, args):
    global playing
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
        return

    play_queue.append(PlayItem(random.choice(TICK_FILES)))

    if not playing:
        playing = True
        next_in_queue()


@cs.add_command(
    'test greeting',
    'Greets the person who writes this in discord',
    show_in_help=False
)
async def test_greeting_command(message, args):
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
    elif len(GREETINGS) == 0:
        await message.channel.send('No greetings loaded')
    else:
        generate_tts(random.choice(GREETINGS).format(name=message.author.display_name))


@cs.add_command(
    'imitate',
    'Imitates a particular person on the server using machine learning',
    arguments=TextFromList(vege_learn.models.keys())
)
async def imitate_command(message, args):
    await message.channel.send(vege_learn.imitate_user(user.lower()))


@client.event
async def on_ready():
    global bot_channel
    print('Bot is ready')

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == bot_channel_name:
                bot_channel = channel


@client.event
async def on_voice_state_update(member, before, after):
    global vc, playing

    if vc is None:  # ignore everything if not connected to VC
        return
    if before.channel == after.channel:  # ignore mutes and un-mutes
        return

    if after.channel == vc.channel:
        if len(GREETINGS) > 0:
            generate_tts(random.choice(GREETINGS).format(name=member.display_name))
    else:
        if len(vc.channel.members) == 1:  # leave if bot is the only one in the chat
            await vc.disconnect()
            vc = None
        else:
            generate_tts('bye {name}'.format(name=member.display_name))


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
