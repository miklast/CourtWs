from typing import Optional

import discord
from discord import app_commands
import requests
import time
import json
import os

baseURL = 'http://www.thebluealliance.com/api/v3/'
header = {'X-TBA-Auth-Key':''}

s = requests.Session() #This prevents us from repeatedly opening and closing a socket + speeds it up.
def getTBA(url):
	return s.get(baseURL + url, headers=header).json()


MY_GUILD = discord.Object(id=)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)



@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# --------
# COMMANDS
# --------

@client.tree.command()
async def add_team(interaction: discord.Interaction, team_number: int):
    #Add a team to the court W's

    with open('courtTeams.txt', 'r') as outfile:
        lines = outfile.readlines()
        for i in lines:
            if(i.strip("\n") == str(team_number)):
                await interaction.response.send_message(f'Team {str(team_number)} is already listed as a court team!')
                return

    with open('courtTeams.txt', 'a') as outfile:        
        outfile.write(str(team_number) + "\n")


    await interaction.response.send_message(f'team {str(team_number)} has been added!')


@client.tree.command()
@app_commands.describe(
    team_number='the team number you are looking up',

)
async def tba_lookup(interaction: discord.Interaction, team_number: int):
    #Grabs basic TBA info about a team.

    teamInfo = getTBA("team/frc" + str(team_number) + "/simple")

    my_embed = discord.Embed(title="Court team " + str(teamInfo["team_number"]) + ", " + teamInfo["nickname"], 
                url ='https://www.thebluealliance.com/team/'+str(team_number), 
                color=46766)
    
    my_embed.set_thumbnail(url='https://frcavatars.herokuapp.com/get_image?team='+str(team_number))
    my_embed.add_field(name='Location',value=teamInfo["city"] + ", " + teamInfo["state_prov"])


    await interaction.response.send_message(embed = my_embed)



    #await interaction.response.send_message(f'Team {teamInfo["team_number"]}, {teamInfo["nickname"]}, from {teamInfo["city"]}, {teamInfo["state_prov"]}.')


@client.tree.command()
@app_commands.describe(
    team_number='the court team you are looking up',

)
async def court_tinfo(interaction: discord.Interaction, team_number: int):
    #Grabs TBA info about A court team. Will include extra info such as next match and W's.

    with open('courtTeams.txt', 'r') as outfile:
        lines = outfile.readlines()
        for i in lines:
            if(i.strip("\n") == str(team_number)):

                teamInfo = getTBA("team/frc" + str(team_number) + "/simple")

                my_embed = discord.Embed(title="Court team " + str(teamInfo["team_number"]) + ", " + teamInfo["nickname"], 
                             url ='https://www.thebluealliance.com/team/'+str(team_number), 
                             color=46766)
    
                my_embed.set_thumbnail(url='https://frcavatars.herokuapp.com/get_image?team='+str(team_number))
                my_embed.add_field(name='Location',value=teamInfo["city"] + ", " + teamInfo["state_prov"])


                await interaction.response.send_message(embed = my_embed)
                return
        await interaction.response.send_message(f'Team {str(team_number)} is not a court team!')

    #await interaction.response.send_message(f'Team {teamInfo["team_number"]}, {teamInfo["nickname"]}, from {teamInfo["city"]}, {teamInfo["state_prov"]}.')


@client.tree.command()
@app_commands.describe(
    team_number='the court team you are looking up',

)
async def court_team_ws(interaction: discord.Interaction, team_number: int):
    #Counts up all W's earned by a specific team in the court during the current season.

    teamInfo = getTBA("team/frc" + str(team_number) + "/awards")
    wins = 0
    finalist = 0
    culture = 0
    awards = 0

    for i in teamInfo:
        #print(i['award_type'])

        if(i['award_type'] == 0 or i['award_type'] == 9) :
            culture+=1
        elif(i['award_type'] == 1):
            wins+=1
        elif(i['award_type'] == 2): 
            finalist+=1
        else:
            awards+=1

    my_embed = discord.Embed(title=f"{str(team_number)}'s W's")
    my_embed.set_thumbnail(url='https://frcavatars.herokuapp.com/get_image?team='+str(team_number))
    my_embed.add_field(name="Wins", value=str(wins), inline=True)
    my_embed.add_field(name="finaLists", value=str(finalist), inline=True)
    my_embed.add_field(name="\u200B", value="\u200B")  # newline
    my_embed.add_field(name="culTure", value=str(culture), inline=True)
    my_embed.add_field(name="aWards", value=str(awards), inline=True)


    await interaction.response.send_message(embed = my_embed)


@client.tree.command()
async def court_total_ws(interaction: discord.Interaction):
    "Counts up all W's earned by the court during the current season."

    my_embed = discord.Embed(title="Court W's")
    # todo: figure out if theres a better way to do thumbnail
    my_embed.set_thumbnail(url='https://i.imgur.com/BueDGHx.png')
    my_embed.add_field(name="Wins", value="test", inline=True)
    my_embed.add_field(name="finaLists", value="test", inline=True)
    my_embed.add_field(name="aWards", value="test", inline=True)


    await interaction.response.send_message(embed = my_embed)

@client.tree.command()
@app_commands.describe(
    team_number='the court team you are looking up',

)
async def nextmatch_team(interaction: discord.Interaction, team_number: int):
    "Shows roughly how long until the next match is for a team."

    teamInfo = getTBA("team/frc" + str(team_number) + "/matches/2023/simple")
    getKeys = getTBA("team/frc" + str(team_number) + "/events/2023/simple")

    for i in getKeys:
        print(str(i["key"]))
        if(str(i["key"]) == "2023arc" or str(i["key"]) =="2023cur" or str(i["key"]) == "2023dal" or str(i["key"]) == "2023gal" 
        or str(i["key"]) ==  "2023hop" or str(i["key"]) == "2023joh" or str(i["key"]) == "2023mil" or str(i["key"]) == "2023new"):
            code = i["key"]
            print("correct" + code)
            break


    exactTeamInfo = getTBA("team/frc" + str(team_number) + "/event/" + str(code) + "/matches/simple")
    matchGet = getTBA("event/" + str(code) + "/insights")
    nextMatchGet = getTBA("team/frc" + str(team_number) + "/event/" + str(code) + "/status")
    nextMatch = nextMatchGet["next_match_key"]
    currentMatch = int(matchGet["qual"]["activation_bonus_rp"][1])/2
    print(nextMatch)
    timeBetween = int(nextMatch[-2:])-int(currentMatch)
    currentUnixTime = time.time()
    print(str(teamInfo[0]["match_number"]))

    for i in exactTeamInfo:
         if(int(i["match_number"]) == int(nextMatch[-2:])):
             print(str(i["predicted_time"]) + " dfsf " + str(i["match_number"])) 
             timeTillMatch = (i["predicted_time"] - time.time())/60

    await interaction.response.send_message(f"Team {str(team_number)} 's next match is in **{int(timeTillMatch)} minutes** (QM{nextMatch[-2:]})")



# The rename decorator allows us to change the display of the parameter on Discord.
# In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# Note that other decorators will still refer to it as `text_to_send` in the code.
@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# This context menu command only works on members
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')

# TBA Testing
# @client.tree.context_menu(name='Team Info')
# async def show_team_info(interaction: discord.Interaction, member: discord.Member):
#     # The format_dt function formats the date time into a human readable representation in the official client
#     await interaction.response.send_message(f'{getTBA("team/frc7461/simple")}')


# This context menu command only works on messages
@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # We're sending this response message with ephemeral=True, so only the command executor can see it
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel()  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)

client.run('')
