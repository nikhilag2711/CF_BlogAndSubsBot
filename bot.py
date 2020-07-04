
import os
import random
import discord
import json
import requests
import re
import datetime

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
        f'{user} is so good.',
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
async def create_channel(ctx, channel_name):
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

@bot.command(name='recent_blogs', help='List user\'s latest 5 blogs within a given upvotes or date range alongwith the tags related to them.', usage='handle [u>=upvotes] [u<=upvotes] [d>=[[dd]mm]yyyy] [d<[[dd]mm]yyyy] [+tags]')
async def blog_of_user(ctx, handle, *args):
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)

    if data['status'] == "FAILED":
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is dumb. (S)he has written no blogs.')
    else:

        rat_ub = 5000
        rat_lb = -5000
        date_ub = datetime.datetime.now()
        date_lb = datetime.datetime(2000, 1, 1)
        tags = []

        for arg in args:
            if arg[0:1] == '+' :
                tags.append(arg[1:])
            elif len(arg) <= 3 :
                await ctx.send('Do not pass wrong parameters.')
                return
            elif arg[0:3] == 'u>=' :
                try:
                    int(arg[3:])
                except ValueError:
                    await ctx.send('The upvotes should be greater than an integer.')
                    pass
                num = int(arg[3:])
                rat_lb = max(rat_lb,num)
            elif arg[0:3] == 'u<=' :
                try:
                    int(arg[3:])
                except ValueError:
                    await ctx.send('The upvotes should be less than an integer.')
                    pass
                num = int(arg[3:])
                rat_ub = min(rat_ub,num)
            elif arg[0:3] == 'd>=':
                if len(arg[3:]) == 4:
                    try:
                        datetime.datetime.strptime(arg[3:], '%Y')
                    except ValueError:
                        await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                        pass
                    date = datetime.datetime.strptime(arg[3:], '%Y')
                    date_lb = max(date, date_lb)
                elif len(arg[3:]) == 6:
                    try:
                        datetime.datetime.strptime(arg[3:], '%m%Y')
                    except ValueError:
                        await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                        pass
                    date = datetime.datetime.strptime(arg[3:], '%m%Y')
                    date_lb = max(date, date_lb)
                elif len(arg[3:]) == 8:
                    try:
                        datetime.datetime.strptime(arg[3:], '%d%m%Y')
                    except ValueError:
                        await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                        pass
                    date = datetime.datetime.strptime(arg[3:], '%d%m%Y')
                    date_lb = max(date, date_lb)
                else :
                    await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                    return
            elif arg[0:2] == 'd<' :
                if len(arg[2:]) == 4:
                    try:
                        datetime.datetime.strptime(arg[2:], '%Y')
                    except ValueError:
                        await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                        pass
                    date = datetime.datetime.strptime(arg[2:], '%Y')
                    date_ub = min(date, date_ub)
                elif len(arg[2:]) == 6:
                    try:
                        datetime.datetime.strptime(arg[2:], '%m%Y')
                    except ValueError:
                        await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                        pass
                    date = datetime.datetime.strptime(arg[2:], '%m%Y')
                    date_ub = min(date, date_ub)
                elif len(arg[2:]) == 8:
                    try:
                        datetime.datetime.strptime(arg[2:], '%d%m%Y')
                    except ValueError:
                        await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                        pass
                    date = datetime.datetime.strptime(arg[2:], '%d%m%Y')
                    date_ub = min(date, date_ub)
                else :
                    await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                    return
            else:
                await ctx.send('Do not pass wrong parameters.')
                return

        stop_id = data['result'][-1]['id']
        var = 0
        ans = []
        while(1):
            latest_blog = data['result'][var]
            blog_date = datetime.datetime.fromtimestamp(latest_blog['creationTimeSeconds'])
            if latest_blog['rating'] <= rat_ub and latest_blog['rating'] >= rat_lb and blog_date >= date_lb and blog_date <= date_ub :
                if len(tags) > 0 :
                    for tag in latest_blog['tags']:
                        for chk in tags:
                            if tag == chk and latest_blog not in ans:
                                ans.append(latest_blog)
                else :
                    ans.append(latest_blog)
            if(data['result'][var]['id'] == stop_id):
                break
            var = var + 1
        
        var = 0
        if len(ans) == 0 :
            embed = discord.Embed(title=f'Error.', color=0x000000)
            embed.add_field(name=f'Codeforces API Error', value=f'There are no blogs present in your given range of {handle}.', inline=False)
            await ctx.channel.send(embed=embed)
        else :
            embed = discord.Embed(title=f'{handle}\'s latest blog list :', color=0x000000)

            for blog in ans:
                lat_blog = f'https://codeforces.com/blog/entry/{blog["id"]}'
                title = re.sub(r'<.*?>', '', blog['title'])
                date = datetime.datetime.fromtimestamp(blog['creationTimeSeconds'])
                var = var+1
                embed.add_field(name=f'{var}. {title}', value=f'Upvotes={blog["rating"]}, Date : {date.strftime("%d/%m/%Y")}, [Link to the blog]({lat_blog})', inline=False)
                if(var==5):
                    break
            
            await ctx.channel.send(embed=embed)

bot.run(TOKEN)
