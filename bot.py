import os
import random
import discord
import json
import requests

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='hello', help='Responds with a random quote for user\'s happiness')
async def make_happy(ctx, user):
    happy_quotes = [
        f'{user} is so cute.',
        f'{user} is so good',
        (
            f'{user} is so cute and '
            f'{user} is so good.'
        ),
    ]

    response = random.choice(happy_quotes)
    await ctx.send(response)

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.command(name='last_blog', help='List user\'s latest blog.')
async def blog_of_user(ctx, handle):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send('Some other error.')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        blog_id = data['result'][0]['id']
        latest_blog = f'https://codeforces.com/blog/entry/{blog_id}'

        await ctx.send(f'{handle}\'s latest blog link : {latest_blog}')

@bot.command(name='last5_blogs', help='List user\'s latest 5 blogs.')
async def blog_of_user(ctx, handle):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send('Some other error.')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        stop_id = data['result'][-1]['id']
        var = 0
        ans = []
        while(len(ans) < 5):
            latest_blog = f'https://codeforces.com/blog/entry/{data["result"][var]["id"]}'
            ans.append(latest_blog)
            if(data['result'][var]['id'] == stop_id):
                break
            var = var + 1

        to_print = f'```\n{handle}\'s latest blog links :\n\n'
        for i in range(len(ans)):
            tmp = f'{i+1} : {ans[i]}\n'
            to_print += tmp
        to_print += '```'

        await ctx.send(to_print)

@bot.command(name='first_blog', help='List user\'s first blog.')
async def blog_of_user(ctx, handle):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send('Some other error.')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        blog_id = data['result'][-1]['id']
        first_blog = f'https://codeforces.com/blog/entry/{blog_id}'

        await ctx.send(f'{handle}\'s first blog link : {first_blog}')

@bot.command(name='first5_blogs', help='List user\'s first 5 blogs.')
async def blog_of_user(ctx, handle):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send('Some other error.')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        stop_id = data['result'][0]['id']
        var = -1
        ans = []
        while(len(ans) < 5):
            latest_blog = f'https://codeforces.com/blog/entry/{data["result"][var]["id"]}'
            ans.append(latest_blog)
            if(data['result'][var]['id'] == stop_id):
                break
            var = var - 1

        to_print = f'```\n{handle}\'s latest blog links :\n\n'
        for i in range(len(ans)):
            tmp = f'{i+1} : {ans[i]}\n'
            to_print += tmp
        to_print += '```'

        await ctx.send(to_print)

bot.run(TOKEN)
