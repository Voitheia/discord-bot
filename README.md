### TODO
- requirements.txt?
- errors
  - capture and return stderr instead of printing it to console
  - actually have error handling
- improve help menu
- auto capture what user implant is running as
  - need some logic for if windows or linux here
  - maybe make implant class instead of using a buncha vars
- figure out packaging this as standalone
- persistence?
- add command to kill implant
- is there a length limit to the command that can be passed thru the bot? just the standard discord msg limit?
- have a message with the list of sessions that gets edited when sessions join/die?
  - will need to figure out how to get only one implant to do that, maybe make a field for the first implant?
  - then what happens if the first implant dies?
  - each time this happens, does the first implant make a thread on this msg to indicate its still alive to the other implants?

### References
https://discordpy.readthedocs.io/en/stable/
