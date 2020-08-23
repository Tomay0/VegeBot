import discord

from discord import FFmpegPCMAudio

from gtts import gTTS

client = discord.Client()

text_channels = []
voice_channels = []

vc = None

play_queue = []
playing = False


def next_in_queue(error):
    global playing, play_queue

    if len(play_queue) == 0:
        playing = False
        return

    text = play_queue.pop(0)

    voice_text = gTTS(text=text, lang='en', slow=False)

    voice_text.save("vege.mp3")

    audio_source = FFmpegPCMAudio('vege.mp3')

    if vc is None:
        playing = False
        play_queue.clear()
        return

    vc.play(audio_source, after=next_in_queue)


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

            play_queue.append(text)
            if not playing:
                playing = True
                next_in_queue(None)
        else:
            await message.channel.send("I'm not in a voice channel. Join a voice channel and type \"vege come here\"")


@client.event
async def on_message_delete(message):
    if message.author.id == 746605769641951313:
        return

    await message.channel.send(
        "Hey " + message.author.mention + ", here's your deleted message:\n" + message.content)

    for attachment in message.attachments:
        try:
            file = await attachment.to_file(use_cached=True)

            await message.channel.send(file=file)
        except discord.errors.NotFound:
            print("Could not post deleted image")


@client.event
async def on_message_edit(before, after):
    await before.channel.send(
        "Hey " + before.author.mention + ", here is the message before it was edited:\n" + before.content)

    for attachment in before.attachments:
        try:
            file = await attachment.to_file(use_cached=True)

            await before.channel.send(file=file)
        except discord.errors.NotFound:
            print("Could not post deleted image")


# Read bot token
# Create a token.txt with your own token if you want to use this bot
token_file = open("token.txt", "r")

client.run(token_file.read())

token_file.close()
