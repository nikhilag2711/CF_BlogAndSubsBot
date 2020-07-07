import os, asyncio, random, discord, json, requests, re, datetime, helper
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='b!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='hello', help='Responds with a random quote about user.')
async def make_happy(ctx, user):
    happy_quotes = [
        f'{user} is bad.',
        f'{user} is good.',
        f'{user} is good as well as bad.'
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

@bot.command(name='create-channel', help='Creates a channel in your Discord server.')
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

@bot.command(name='recent_blogs', help='List user\'s latest 5 blogs within a given upvotes or date range alongwith the tags related to them.', usage='handle [u>=upvotes] [u<=upvotes] [d>=[[dd]mm]yyyy] [d<[[dd]mm]yyyy] [+tags...]')
async def blog_of_user(ctx, handle, *args) :
    url = f'https://codeforces.com/api/user.blogEntries?handle={handle}'
    obj = requests.get(url)
    data = json.loads(obj.text)
    url = f'https://codeforces.com/api/user.info?handles={handle}'
    obj = requests.get(url)
    data2 = json.loads(obj.text)

    if data['status'] == "FAILED" or data2['status'] == "FAILED":
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} is so dumb. (S)he has written no blogs.')
    else:
        pic = "https:" + data2['result'][0]['titlePhoto']
        rat_ub, rat_lb = 5000, -5000
        date_ub, date_lb = datetime.datetime.now(), datetime.datetime(2000, 1, 1)
        tags = []

        for arg in args:
            if arg[0:1] == '+' :
                tags.append(arg[1:])
            elif len(arg) <= 3 :
                await ctx.send('Invalid parameters. Please try again with correct parameters.')
                return
            elif arg[0:3] == 'u>=' :
                if helper.isValidInteger(arg[3:]) == False :
                    await ctx.send('The upvotes range should be an integer.')
                    return
                else :
                    rat_lb = max(rat_lb, int(arg[3:]))
            elif arg[0:3] == 'u<=' :
                if helper.isValidInteger(arg[3:]) == False :
                    await ctx.send('The upvotes range should be an integer.')
                    return
                else :
                    rat_ub = min(rat_ub, int(arg[3:]))
            elif arg[0:3] == 'd>=':
                if helper.isValidDate(arg[3:]) == False:
                    await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                    return
                else :
                    date_lb = max(helper.isValidDate(arg[3:]), date_lb)
            elif arg[0:2] == 'd<' :
                if helper.isValidDate(arg[2:]) == False:
                    await ctx.send('The date should in DDMMYYYY or MMYYYY or YYYY format.')
                    return
                else :
                    date_ub = min(helper.isValidDate(arg[2:]), date_ub)
            else:
                await ctx.send('Invalid parameters. Please try again with correct parameters.')
                return

        stop_id, var = data['result'][-1]['id'], 0
        ans = []
        while(1):
            latest_blog = data['result'][var]
            blog_date = datetime.datetime.fromtimestamp(latest_blog['creationTimeSeconds'])
            if latest_blog['rating'] <= rat_ub and latest_blog['rating'] >= rat_lb and blog_date >= date_lb and blog_date <= date_ub :
                if len(tags) > 0 :
                    blg = helper.tag_match(tags, latest_blog)
                    if blg != False and blg not in ans:
                        ans.append(blg)
                else :
                    ans.append(latest_blog)
            if(data['result'][var]['id'] == stop_id):
                break
            var = var + 1
        
        var = 0
        if len(ans) == 0 :
            embed = discord.Embed(title=f'Error.', color=0x000000)
            embed.add_field(name=f'Invalid parameters', value=f'There are no blogs present in your given range of {handle}.', inline=False)
            await ctx.channel.send(embed=embed)
        else :
            embed = discord.Embed(title=f'{handle}\'s latest blog list :', color=0x000000)
            embed.set_thumbnail(url=pic)
            for blog in ans:
                lat_blog = f'https://codeforces.com/blog/entry/{blog["id"]}'
                title = re.sub(r'<.*?>', '', blog['title'])
                date = datetime.datetime.fromtimestamp(blog['creationTimeSeconds'])
                var = var+1
                embed.add_field(name=f'{var}. {title}', value=f'Upvotes={blog["rating"]}, Date : {date.strftime("%d/%m/%Y")}, [Link to the blog]({lat_blog})', inline=False)
                if(var==5):
                    break
            
            await ctx.channel.send(embed=embed)

@bot.command(name='status', help='Returns the problems solved by a user in a specific contest.', usage='handle id [+ac] [+contest] [+practice] [+unofficial] [+virtual]')
async def userContestStatus(ctx, handle, id, *args) :
    if helper.isValidInteger(id) == False:
        await ctx.send('Specify the contest id in integer format only.')
        return
    
    id = helper.isValidInteger(id)
    url = f'https://codeforces.com/api/contest.status?contestId={id}&handle={handle}&from=1'
    obj = requests.get(url)
    data = json.loads(obj.text)
    
    if data['status'] == "FAILED" :
        await ctx.send(f'{data["comment"]}')
    elif len(data['result']) == 0:
        await ctx.send(f'{handle} has made no submissions yet.')
    else:
        stop_id = data['result'][-1]['id']
        var = 0
        ans = []
        ac, official, virtual, practice, unoff = False, False, False, False, False

        for arg in args:
            if arg == '+ac':
                ac = True
            elif arg == '+contest':
                official = True
            elif arg == '+virtual':
                virtual = True
            elif arg == '+practice':
                practice = True
            elif arg == '+unofficial':
                unoff = True
            else :
                await ctx.send('Invalid arguments. Please enter correct arguments and then try again.')
                return

        while(1):
            if data['result'][var]['contestId'] == id:
                ans.append(data['result'][var])
            if data['result'][var]['id'] == stop_id:
                break
            var = var+1

        embeds = []
        if len(ans) == 0:
            await ctx.send(f'{handle} has made no submissions in the contest having id = {id}.')
        else:
            var = 0
            for subs in ans:
                number = subs['problem']['index']
                name = subs['problem']['name']
                rat = subs['problem']['rating']
                tag = subs['problem']['tags']
                part = subs['author']['participantType']
                verdict = subs['verdict']

                tags = ""
                for t in tag :
                    if tags == "" :
                        tags += t
                    else :
                        tags += ', ' + t

                num = helper.check_status(ac, official, virtual, practice, unoff, verdict, part)
                if num == 1:
                    if var%5 == 0:
                        embed = discord.Embed(title=f'{handle}\'s latest submissions in Contest {id} :', color=0x000000)
                        embeds.append(embed)
                    embeds[var//5].add_field(name=f'{number}. {name} [Rating = {rat}]', value=f'Tags : {tags}\nVerdict : {verdict}, Participation : {part}', inline=False)
                    var = var + 1
                if num == 2:
                    if var%5 == 0:
                        embed = discord.Embed(title=f'{handle}\'s latest submissions in Contest {id} :', color=0x000000)
                        embeds.append(embed)
                    embeds[var//5].add_field(name=f'{number}. {name}', value=f'Verdict : {verdict}, Participation : {part}', inline=False)
                    var = var + 1
            
            if var%5 == 0:
                var = var // 5
            else :
                var = var // 5 + 1
            i = 1
            for embed in embeds :
                embed.set_footer(text=f'Page : {i}/{var}')
                i = i+1

            if var == 0:
                await ctx.send(f'{handle} do not have any submission in the contest {id} with the given parameters.')
            else:
                message = await ctx.channel.send(embed=embeds[0])
                emojis = ['\u23ee', '\u25c0', '\u25b6', '\u23ed']
                for emoji in emojis:
                    await message.add_reaction(emoji)

                i, emoji = 0, ''
                while True :
                    if emoji == '\u23ee' :
                        i = 0
                        await message.edit(embed = embeds[i])
                    if emoji == '\u25c0' :
                        if i > 0 :
                            i = i - 1
                            await message.edit(embed=embeds[i])
                    if emoji == '\u25b6' :
                        if i < len(embeds) - 1 :
                            i = i + 1
                            await message.edit(embed=embeds[i])
                    if emoji == '\u23ed' :
                        i = len(embeds) - 1
                        await message.edit(embed=embeds[i])
                    
                    def predicate(message):
                        def check(reaction, user):
                            if reaction.message.id != message.id or user == bot.user:
                                return False
                            for em in emojis :
                                if reaction.emoji == em :
                                    return True
                            return False
                        return check
                    
                    try:
                        react, user = await bot.wait_for('reaction_add', timeout=15, check=predicate(message))
                    except asyncio.TimeoutError:
                        break
                    emoji = str(react)
                    await message.remove_reaction(emoji, member=user)

                for emoji in emojis:
                    await message.clear_reaction(emoji)

bot.run(TOKEN)
