import os
import random
import discord
import json
import requests
import re

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
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        blog_id = data['result'][0]['id']
        embed = discord.Embed(title=f'{handle}\'s latest blog :', color=0x000000)
        latest_blog = f'https://codeforces.com/blog/entry/{blog_id}'
        title = re.sub(r'<.*?>', '', data['result'][0]['title'])
        embed.add_field(name=f'{title}', value=f'Upvotes={data["result"][0]["rating"]}, [Link to the blog]({latest_blog})', inline=False)

        await ctx.channel.send(embed=embed)

@bot.command(name='first_blog', help='List user\'s first blog.')
async def blog_of_user(ctx, handle):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        blog_id = data['result'][-1]['id']
        embed = discord.Embed(title=f'{handle}\'s latest blog :', color=0x000000)
        title = re.sub(r'<.*?>', '', data['result'][-1]['title'])
        first_blog = f'https://codeforces.com/blog/entry/{blog_id}'
        embed.add_field(name=f'{title}', value=f'Upvotes={data["result"][-1]["rating"]}, [Link to the blog]({first_blog})', inline=False)
        
        await ctx.channel.send(embed=embed)

@bot.command(name='last5_blogs', help='List user\'s latest 5 blogs.')
async def blog_of_user(ctx, handle, upvotes:int = None):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        stop_id = data['result'][-1]['id']
        var = 0
        ans = []
        embed = discord.Embed(title=f'{handle}\'s latest blog list :', color=0x000000)
        while(len(ans) < 5):
            latest_blog = f'https://codeforces.com/blog/entry/{data["result"][var]["id"]}'
            title = re.sub(r'<.*?>', '', data['result'][var]['title'])
            if upvotes is not None :
                if data['result'][var]['rating'] >= upvotes:
                    embed.add_field(name=f'{len(ans)+1}. {title}', value=f'Upvotes={data["result"][var]["rating"]}, [Link to the blog]({latest_blog})', inline=False)
                    ans.append(latest_blog)
            else:
                embed.add_field(name=f'{len(ans)+1}. {title}', value=f'Upvotes={data["result"][var]["rating"]}, [Link to the blog]({latest_blog})', inline=False)
                ans.append(latest_blog)
            if(data['result'][var]['id'] == stop_id):
                break
            var = var + 1

        if upvotes is not None and len(ans) == 0:
            await ctx.send(f'{handle} have no blog having upvotes >= {upvotes}')
            return

        await ctx.channel.send(embed=embed)

@bot.command(name='first5_blogs', help='List user\'s first 5 blogs.')
async def blog_of_user(ctx, handle):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:
        stop_id = data['result'][0]['id']
        var = -1
        ans = []
        embed = discord.Embed(title=f'{handle}\'s latest blog list :', color=0x000000)
        while(len(ans) < 5):
            latest_blog = f'https://codeforces.com/blog/entry/{data["result"][var]["id"]}'
            title = re.sub(r'<.*?>', '', data['result'][var]['title'])
            embed.add_field(name=f'{len(ans)+1}. {title}', value=f'Upvotes={data["result"][var]["rating"]}, [Link to the blog]({latest_blog})', inline=False)
            ans.append(latest_blog)
            if(data['result'][var]['id'] == stop_id):
                break
            var = var - 1

        await ctx.channel.send(embed=embed)

bot.run(TOKEN)
