import discord
import random
import os
from discord import FFmpegPCMAudio
from gtts import gTTS
from datetime import datetime
from sys import argv
from os import listdir
from os.path import isfile, join
import tweepy
import requests
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


@async_to_sync
async def send_channel_message(message):
    try:
        print("sending message: " + message)
        if bot_channel is not None:
            await bot_channel.send(message)
    except:
        print("Could not send message..")


# listens to twitter tweets
class TwitterListener(tweepy.StreamListener):
    def on_status(self, status):

        if 'retweeted_status' not in status._json and status._json['in_reply_to_status_id'] is None and \
                status._json['user']['id_str'] in following:
            if hasattr(status, 'extended_tweet'):
                send_channel_message(status.extended_tweet['full_text'])
            else:
                send_channel_message(status.text)

    def on_error(self, status_code):
        return True


# Twitter API
if os.path.exists('twitter_tokens.txt') and os.path.exists('following.txt'):
    with open('twitter_tokens.txt', 'r') as twitter_tokens:
        TOKENS = twitter_tokens.readlines()

        auth = tweepy.OAuthHandler(TOKENS[0].strip(), TOKENS[1].strip())
        auth.set_access_token(TOKENS[2].strip(), TOKENS[3].strip())

        api = tweepy.API(auth)
        streamListener = TwitterListener()
        stream = tweepy.Stream(auth=api.auth, listener=streamListener)

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


def send_message_to_database(message):
    json = {
        'id': message.id,
        'channel_name': message.channel.name,
        'channel_id': message.channel.id,
        'author_name': message.author.name,
        'author_id': message.author.id,
        'guild_name': message.guild.name,
        'guild_id': message.guild.id,
        'time': message.created_at.isoformat(),
        'text': message.content,
        'remove': False
    }

    response = requests.post('https://ai7pkjomr4.execute-api.ap-southeast-2.amazonaws.com/dev', json=json)


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
    aliases=['go', 'leave', 'fuck off', 'alt-f4']
)
async def leave_vc_command(message, args):
    global vc
    if vc is None:
        return

    await vc.disconnect()
    vc = None


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


@cs.add_command('reset stats db', 'reset message statistics database', show_in_help=False)
async def reset_stats_db(message, args):
    #response = requests.put('https://ai7pkjomr4.execute-api.ap-southeast-2.amazonaws.com/dev', json={'remove': True})

    for guild in client.guilds:
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.read_messages:
                async for message in channel.history(limit=None):
                    print('sending message: ' + message.content)
                    send_message_to_database(message)


@cs.add_command('get stats', 'test get stats thingy', show_in_help=False)
async def get_stats(message, args):
    json = {"type": "num_messages",
            "time_interval": "alltime",
            "guild": 746609150842372138,
            "timezone": "Pacific/Auckland"}

    response = requests.post('https://ai7pkjomr4.execute-api.ap-southeast-2.amazonaws.com/dev/stats', json=json)

    await message.channel.send(response.content)


@client.event
async def on_ready():
    global bot_channel
    print('Bot is ready')

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == bot_channel_name:
                bot_channel = channel


@client.event
async def on_message(message):
    send_message_to_database(message)
    await cs.on_message(message)


@client.event
async def on_voice_state_update(member, before, after):
    global vc, playing

    # ignore everything if not connected to VC
    # ignore mutes and un-mutes
    # ignore state changes for vegebot
    if vc is None or before.channel == after.channel or member.id == client.user.id:
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
    json = {
        'id': message.id,
        'remove': True
    }
    response = requests.post('https://ai7pkjomr4.execute-api.ap-southeast-2.amazonaws.com/dev', json=json)


@client.event
async def on_message_edit(before, after):
    send_message_to_database(after)


# Read bot token
with open(argv[1] if len(argv) > 1 else 'token.txt') as token_file:
    client.run(token_file.read())
