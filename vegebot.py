import discord

from discord.ext import commands

bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.command()
async def help(ctx):
    await ctx.send("0800 543 354")

bot.run("NzQ2NjA1NzY5NjQxOTUxMzEz.X0Cwzg.b2jXUMwWG38VgMfzHiHvx70jtAk")