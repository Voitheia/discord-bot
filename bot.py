import time
from subprocess import check_output

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)
max_msg_size = 2000

def get_datetime():
	return time.strftime('[%Y-%m-%d %H:%M:%S]')

def log_msg(msg):
	print(f'{get_datetime()} {msg}')

async def send_msg(ctx, msg):
	if len(msg) >= max_msg_size:
		await ctx.send(f'{msg[:max_msg_size]}')
		await send_msg(ctx, msg[max_msg_size:])
	else:
		await ctx.send(f'{msg}')

@bot.event
async def on_ready():
	log_msg(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	log_msg(f'The message\'s content was {message.content}')
	await bot.process_commands(message)

@bot.command()
async def ping(ctx):
	'''
	This text will be shown in the help command
	'''

	# Get the latency of the bot
	latency = bot.latency  # Included in the Discord.py library
	# Send it to the user
	await ctx.send(f'Current latency: {latency}s')

@bot.command(rest_is_raw=True)
async def cmd(ctx, *, arg):
	arg = arg[1::]
	log_msg(f'Command recieved: {arg}')
	await send_msg(ctx, f'Command sent: {arg}\n\nOutput: {check_output(arg, shell=True).decode()}')
	log_msg(f'Finished processing command: {arg}')

bot.run("MTI3NTgyNTA2MTM3ODY1ODM2Nw.G1e8mP.3hhbRTZ6dpz8oefx5bxB9MOtBbA4KB2a6-TBHs")  # Where 'TOKEN' is your bot token