import random
import os
import logging
import yaml
from discord import FFmpegPCMAudio
from gtts import gTTS
from os import getenv
from commands import *
from database import PostgRESTDatabase
from asgiref.sync import async_to_sync

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

client = discord.Client()
cs = CommandSystem('vege ', client)

vc = None
play_queue = []
playing = False
play_id = 0

greetings = []
database = None

# Load greetings from config
try:
    with open("config.yml", "r") as f:
        config_data = yaml.load(f, Loader=yaml.FullLoader)

        if 'greetings' in config_data:
            greetings = config_data['greetings']
except FileNotFoundError:
    logging.warning("Could not find config.yml")
    logging.warning("Some features may not work properly")
except yaml.scanner.ScannerError:
    logging.warning("config.yml has invalid syntax")
    logging.warning("Some features may not work properly")

# Load database
if (url := getenv('POSTGREST_URL')) is not None and (p_token := getenv('POSTGREST_TOKEN')) is not None:
    database = PostgRESTDatabase(url, p_token)
else:
    logging.warning("Database token and url not provided.")
    logging.warning("Include your PostgREST Authorization token as the environment variable: POSTGREST_TOKEN")
    logging.warning("Include your PostgREST URL as the environment variable: POSTGREST_URL")


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


async def reset_database():
    global database

    if database is None:
        logging.warning('Database was not loaded, so could not be reset')
        return

    database.clear_database()

    all_messages = []
    for guild in client.guilds:
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.read_messages:

                async for m in channel.history(limit=None):
                    all_messages.append(m)

    database.add_messages(all_messages)

    logging.info("Database Reset")


@cs.add_command('say', 'Will say out loud any text you give it', arguments=AnyText())
async def say_command(message, args):
    if vc is None:
        await message.channel.send('I must be in a voicechat if you want me to say that.')
    elif len(args) > 300:
        await message.channel.send('There is a character limit of 300 for TTS messages here')
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
    else:
        role = discord.utils.get(message.guild.roles, name=role_name)

    if role not in message.author.roles:
        await message.author.add_roles(role)

    await role.edit(colour=discord_color)
    await message.channel.send('Done')


@cs.add_command(
    'test greeting',
    'Greets the person who writes this in discord',
    show_in_help=False
)
async def test_greeting_command(message, _):
    if vc is None:
        await message.channel.send('Can\'t. I\'m not in a voice channel')
    elif len(greetings) == 0:
        await message.channel.send('No greetings loaded')
    else:
        generate_tts(random.choice(greetings).format(name=message.author.display_name))


@cs.add_command(
    'stats',
    'Display stats about the server',
    show_in_help=True,
    arguments=AtLeast(TextFromList(['usermessages', 'channelmessages']))
)
async def vege_stats_command(message, args):
    args_split = args.split(" ")

    if len(args_split) < 1:
        return

    stat_type = args_split[0].lower().replace("_", "")
    scope_type = "guild" if len(args_split) == 1 else args_split[1]

    if database is None:
        await message.channel.send('Sorry, I could not connect to the database at this time...')

    if stat_type == 'usermessages':
        if scope_type == 'channel':
            # Obtain JSON representation of the number of messages users have in this channel
            user_messages_json = database.get_data(
                f"usermessagesbychannel?guild_id=eq.{message.guild.id}&channel_id=eq.{message.channel.id}")
            category = message.channel.name
        else:
            # Obtain JSON representation of the number of messages this user have in this server
            user_messages_json = database.get_data(f"usermessagesbyguild?guild_id=eq.{message.guild.id}")
            category = message.guild.name

        # Send sorted list of top users
        user_messages_dict = {x['user_id']: {'name': x['user_name'], 'count': x['count']} for x in user_messages_json}
        users_sorted = sorted([x['user_id'] for x in user_messages_json], key=lambda x: -user_messages_dict[x]['count'])

        user_list_string = f'Top Users for {category}:\n'

        for i, u_id in enumerate(users_sorted):
            user_list_string += f'#{i + 1}: {user_messages_dict[u_id]["name"]} ({user_messages_dict[u_id]["count"]})\n'

        await message.channel.send(user_list_string)
    elif stat_type == 'channelmessages':
        # Send sorted list of top channels
        channel_messages_json = database.get_data(f"messagesbychannel?guild_id=eq.{message.guild.id}")

        channel_messages_dict = {x['channel_id']: {'name': x['channel_name'], 'count': x['count']} for x in
                                 channel_messages_json}
        channels_sorted = sorted([x['channel_id'] for x in channel_messages_json],
                                 key=lambda x: -channel_messages_dict[x]['count'])

        channel_list_string = f'Top Channels for {message.guild.name}:\n'

        for i, c_id in enumerate(channels_sorted):
            channel_list_string += f'#{i + 1}: {channel_messages_dict[c_id]["name"]}' \
                                   f' ({channel_messages_dict[c_id]["count"]})\n'

        await message.channel.send(channel_list_string)


@client.event
async def on_ready():
    logging.info('Resetting database..')
    # Reset the database
    print("starting reset")
    await reset_database()
    print("finished reset")

    logging.info('VegeBot is ready')
    print("Vege is ready")


@client.event
async def on_voice_state_update(member, before, after):
    global vc, playing

    # ignore everything if not connected to VC
    # ignore mutes and un-mutes
    # ignore state changes for vegebot
    if vc is None or before.channel == after.channel or member.id == client.user.id:
        return

    if after.channel == vc.channel:
        if len(greetings) > 0:
            generate_tts(random.choice(greetings).format(name=member.display_name))
    else:
        if len(vc.channel.members) == 1:  # leave if bot is the only one in the chat
            await vc.disconnect()
            vc = None
        else:
            generate_tts('bye {name}'.format(name=member.display_name))


@client.event
async def on_message(message):
    await cs.on_message(message)
    if database is not None:
        database.add_message(message)


@client.event
async def on_message_delete(message):
    if database is not None:
        database.delete_message(message)


@client.event
async def on_message_edit(_, after):
    if database is not None:
        database.add_message(after)


logging.info("Preparing VegeBot...")

if (token := getenv('DISCORD_TOKEN')) is not None:
    client.run(token)
else:
    logging.critical("No discord token found")
