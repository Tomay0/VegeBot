import discord

from discord.ext import commands

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.command()
async def helpplease(ctx):
    await ctx.send("0800 543 354")

# Read bot token
# Create a token.txt with your own token if you want to use this bot
token_file = open("token.txt", "r")

bot.run(token_file.read())

token_file.close()