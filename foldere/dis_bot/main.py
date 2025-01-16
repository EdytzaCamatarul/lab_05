import discord  # base discord module
import os  # environment variables
import inspect  # call stack inspection
import random  # dumb random number generator

import json
import yt_dlp
from discord.ext import commands  # Bot class and utils


################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}

voice_clients = {}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug': ('\033[34m', '-'),
        'info': ('\033[32m', '*'),
        'warning': ('\033[33m', '?'),
        'error': ('\033[31m', '!'),
    }

    # internal ansi codes
    _extra_ansi = {
        'critical': '\033[35m',
        'bold': '\033[1m',
        'unbold': '\033[2m',
        'clear': '\033[0m',
    }

    # get information about call site
    caller = inspect.stack()[1]

    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
              (_extra_ansi['critical'], _extra_ansi['bold'],
               caller.function, caller.lineno,
               _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return

    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
          (_extra_ansi['bold'], *dsp_sel[level],
           caller.function, caller.lineno,
           _extra_ansi['unbold'], msg, _extra_ansi['clear']))


################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

# bot instantiation
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')


# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return

    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')

    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)


# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))

@bot.command(brief='Join your voice channel')
async def join(ctx):
    if ctx.author.voice.channel is None:
        return

    await ctx.author.voice.channel.connect()

@bot.command(brief='Leave your voice channel')
async def leave(ctx):
    if ctx.voice_client is None:
        return
    await ctx.voice_client.disconnect()

    
    
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.mp3',  # Temporary file
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info['title']  # Return the title for acknowledgment




# Play command to play a YouTube link
@bot.command()
async def play(ctx, url):
    guild_id = ctx.guild.id
   
    await ctx.send("Downloading and processing the audio. Please wait...")
   
    title = download_audio(url)
    source = discord.FFmpegPCMAudio('song.mp3.mp3')
    await ctx.voice_client.play(source, after=lambda e: print(f"Finished playing: {e}"))
    await ctx.send(f"Now playing: {title}")




# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))


################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':
    token = '{enter token here}'
    bot.run(token)
