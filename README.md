## CDE '24 Discord Bot C2
Python based discord bot intended to be run as an implant on windows or linux. Able to run commands through python's `check_output` function and return output back to the discord server in a response thread to the command message. Also able to manage a "sessions" text channel where the bot instances will heartbeat, post their info, and react to stale or dead implants. The script expected a file named `token.txt` to exist along side it and to contain a discord bot token in order for the bot to run.

### Commands
All commands are prefixed with `>`.

`>cmd`
- run a command on a or multiple implants
  - `>cmd [FLAG] [IMPLANT_ID] [COMMAND]`
- flags:
  - `-i`
    - target an individual implant for your command, using that implant's id
    - ex: `>cmd -i 233ae396 hostname`
  - `-a`
    - target all implants
  - `-w`
    - target all windows implants
  - `-l`
    - target all linux implants (this might include firewalls too? unsure)
- notes:
  - this command should not need quotes after the implant id, everything after the id will be considered part of the command

`>change_id`
- change the id of an implant
  - `>change_id [IMPLANT_ID] [NEW_IMPLANT_ID]`
- ex: `>change_id 233ae396 T12DC`
- notes:
  - this command needs quotes after the implant id if you want spaces in your id

`>sessions`
- list the active sessions
  - `>sessions`

`>note`
- add a note to an implant
  - `>note [IMPLANT_ID] [NOTE]`
- ex: `>note 233ae396 "this team is cringe"`
- notes:
  - this command needs quotes after the implant id if you want spaces in your note

`>kill`
- kill an implant
  - `>kill [IMPLANT_ID]`
- notes:
  - the implant will respond with a 💀 emoji when it has received the command

`>ping`
- get the ping of the implants
  - `>ping`

### Sessions channel
Reaction emojis and minute for each state are configurable at the top of the python script.

Default values:
- good_react = '🟩'
  - reaction if an implant is alive
- mins_stale = 2
  - number of minutes since last heartbeat for an implant to be considered stale
- stale_react = '🟨'
  - reaction if an implant is stale
- mins_dead = 5
  - number of minutes since last heartbeat for an implant to be considered dead
- dead_react = '🟥'
  - reaction if an implant is dead
- mins_remove = 10
  - number of minutes since last heartbeat for an implant's entry in the sessions channel to get removed

### TODO
- implement way to target multiple implants at once
- look into creating custom groupings of implants
  - array field in Implant class?
  - when someone adds an implant to a group that group id goes into the array or something like that
- figure out packaging this as standalone
- persistence?

- requirements.txt?
- improve help menu
- is there a length limit to the command that can be passed thru the bot? just the standard discord msg limit?

### References
https://discordpy.readthedocs.io/en/stable/


`cd .\source\repos\Voitheia\discord-bot\; .\venv\Scripts\Activate.ps1; python .\bot.py`
