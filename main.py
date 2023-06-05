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

    print(f"LOGGING: Court team add attemped, team {team_number} added by {interaction.user}")

    if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
        print("ryan is banned from the bot until i say otherwise")
        await interaction.followup.send("Ryan is banned from the bot")
        return

    with open('courtTeams.txt', 'r') as outfile:
        lines = outfile.readlines()
        for i in lines:
            if(i.strip("\n") == str(team_number)):
                await interaction.response.send_message(f'Team {str(team_number)} is already listed as a court team!')
                return

    #with open('courtTeams.txt', 'a') as outfile:        
        #outfile.write(str(team_number) + "\n")


    await interaction.response.send_message(f'team {str(team_number)} has been added!')


@client.tree.command()
@app_commands.describe(
    team_number='the team number you are looking up',

)
async def tba_lookup(interaction: discord.Interaction, team_number: int):
    #Grabs basic TBA info about a team.

    print(f"LOGGING: TBA Lookup invoked, team {team_number} searched by {interaction.user}")

    if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
        print("ryan is banned from the bot until i say otherwise")
        await interaction.followup.send("Ryan is banned from the bot")
        return

    teamInfo = getTBA("team/frc" + str(team_number) + "/simple")

    my_embed = discord.Embed(title="Court team " + str(teamInfo["team_number"]) + ", " + teamInfo["nickname"], 
                url ='https://www.thebluealliance.com/team/'+str(team_number), 
                color=46766)
    
    my_embed.set_thumbnail(url='https://frcavatars.herokuapp.com/get_image?team='+str(team_number))
    my_embed.add_field(name='Location',value=teamInfo["city"] + ", " + teamInfo["state_prov"])


    await interaction.response.send_message(embed = my_embed)


@client.tree.command()
@app_commands.describe(
    team_number='the court team you are looking up',

)
async def court_tinfo(interaction: discord.Interaction, team_number: int):
    #Grabs TBA info about A court team. Will include extra info such as next match and W's.

    print(f"LOGGING: court team info invoked, team {team_number} searched by {interaction.user}")

    if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
        print("ryan is banned from the bot until i say otherwise")
        await interaction.followup.send("Ryan is banned from the bot")
        return

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



@client.tree.command()
@app_commands.describe(
    team_number='the court team you are looking up',

)
async def court_team_ws(interaction: discord.Interaction, team_number: int):
    #Counts up all W's earned by a specific team in the court during the current season.

    print(f"LOGGING: court team W's invoked, court team {team_number} searched by {interaction.user}")

    if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
        print("ryan is banned from the bot until i say otherwise")
        await interaction.followup.send("Ryan is banned from the bot")
        return

    teamInfo = getTBA("team/frc" + str(team_number) + "/awards")
    wins = 0
    finalist = 0
    culture = 0
    awards = 0

    for i in teamInfo:

        if(i['award_type'] == 0 or i['award_type'] == 9) :
            culture+=1
        elif(i['award_type'] == 1):
            wins+=1
        elif(i['award_type'] == 2): 
            finalist+=1
        else:
            awards+=1

    my_embed = discord.Embed(title=f"{str(team_number)}'s historical W's")
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

    await interaction.response.defer()
    
    if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
        print("ryan is banned from the bot until i say otherwise")
        await interaction.followup.send("Ryan is banned from the bot")
        return
    
    wins = 0
    finalist = 0
    culture = 0
    awards = 0
    
    with open('courtTeams.txt', 'r') as outfile:
        lines = outfile.readlines()
        for i in lines:
            i=str(i).strip('\n') 
    
            teamInfo = getTBA("team/frc" + str(i) + "/awards")

            for i in teamInfo:

                if(i['award_type'] == 0 or i['award_type'] == 9) :
                    culture+=1
                elif(i['award_type'] == 1):
                    wins+=1
                elif(i['award_type'] == 2): 
                    finalist+=1
                else:
                    awards+=1

    my_embed = discord.Embed(title="Court historical W's")
    # todo: figure out if theres a better way to do thumbnail
    my_embed.set_thumbnail(url='https://i.imgur.com/BueDGHx.png')
    my_embed.add_field(name="Wins", value=wins, inline=True)
    my_embed.add_field(name="finaLists", value=finalist, inline=True)
    my_embed.add_field(name="aWards", value=awards, inline=True)


    await interaction.followup.send(embed = my_embed)


@client.tree.command()
async def court_year_ws(interaction: discord.Interaction, year: int):
    "Counts up all W's earned by the court during the current season."

    await interaction.response.defer()
    
    if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
        print("ryan is banned from the bot until i say otherwise")
        await interaction.followup.send("Ryan is banned from the bot")
        return
    
    if int(year) < 1992 or int(year) > 2023:
        print("invalid year asked")
        await interaction.followup.send(f"{year} is not a valid FRC season")
        return
    
    wins = 0
    finalist = 0
    culture = 0
    awards = 0
    
    with open('courtTeams.txt', 'r') as outfile:
        lines = outfile.readlines()
        for i in lines:
            i=str(i).strip('\n') 
            teamInfo = getTBA("team/frc" + str(i) + "/awards/" + str(year))

            for i in teamInfo:


                if(i['award_type'] == 0) :
                    print(f"{i['award_type']} Culture")
                    wins+=1
                elif(i['award_type'] == 1):
                    print(f"{i['award_type']} win")
                    wins+=1
                elif(i['award_type'] == 2): 
                    finalist+=1
                else:
                    awards+=1

    my_embed = discord.Embed(title=f"Court W's for {year}")
    # todo: figure out if theres a better way to do thumbnail
    my_embed.set_thumbnail(url='https://i.imgur.com/BueDGHx.png')
    my_embed.add_field(name="Wins", value=wins, inline=True)
    my_embed.add_field(name="finaLists", value=finalist, inline=True)
    my_embed.add_field(name="aWards", value=awards, inline=True)


    await interaction.followup.send(embed = my_embed)


@client.tree.command()
@app_commands.describe(
    team_number='the court team you are looking up',

)
async def nextmatch_team(interaction: discord.Interaction, team_number: int):
    "Shows roughly how long until the next match is for a team."
    try:
        print(f"LOGGING: next match invoked, team {team_number} searched by {interaction.user}")
        await interaction.response.defer()

        if str(interaction.user) == "firecrafty#1018": #firecrafty#1018
            print("ryan is banned from the bot until i say otherwise")
            await interaction.followup.send("Ryan is banned from the bot")
            return


        #teamInfo = getTBA("team/frc" + str(team_number) + "/matches/2023/simple")

        getKeys = getTBA("team/frc" + str(team_number) + "/events/2023/simple")
        timeTillMatch = 0

        for i in getKeys:
            #print(str(i["key"]))
            if(str(i["key"]) == "2023arc" or str(i["key"]) =="2023cur" or str(i["key"]) == "2023dal" or str(i["key"]) == "2023gal" 
            or str(i["key"]) ==  "2023hop" or str(i["key"]) == "2023joh" or str(i["key"]) == "2023mil" or str(i["key"]) == "2023new" or str(i["key"]) =="2023cmptx"):
                code = i["key"]
                #print("correct" + code)
                break


        exactTeamInfo = getTBA("team/frc" + str(team_number) + "/event/" + str(code) + "/matches/simple")
        # matchGet = getTBA("event/" + str(code) + "/insights")
        nextMatchGet = getTBA("team/frc" + str(team_number) + "/event/" + str(code) + "/status")
        nextMatch = nextMatchGet["next_match_key"]

        ######
        #QUALS
        ######
          
        if nextMatchGet == "qm":
            # currentMatch = int(matchGet["qual"]["activation_bonus_rp"][1])/2
            print(f"next match: {nextMatch}")

            for i in exactTeamInfo:
                if(int(i["match_number"]) == int(nextMatch[10:])):
                    timeTillMatch = (i["predicted_time"] - time.time())/60
                    blueAlliance = str(i["alliances"]["blue"]["team_keys"]).translate({ord(i): None for i in "frc'[]"})
                    redAlliance = str(i["alliances"]["red"]["team_keys"]).translate({ord(i): None for i in "frc'[]"})

                    if str(team_number) in blueAlliance:
                        blueAlliance = blueAlliance.replace(f"{str(team_number)}", f"**{str(team_number)}**")
                        embed_color = 40151
                    else:
                        redAlliance = redAlliance.replace(f"{str(team_number)}", f"**{str(team_number)}**")
                        embed_color = 15539236


            my_embed = discord.Embed(title=f"Team {team_number}'s next match is in {int(timeTillMatch)} minutes", description=f"next match: **{nextMatch[8:]}**", color=int(embed_color))
            my_embed.add_field(name="Red alliance", value=redAlliance)
            my_embed.add_field(name="Blue alliance", value=blueAlliance)
            my_embed.set_thumbnail(url='https://frcavatars.herokuapp.com/get_image?team='+str(team_number))


            #await interaction.followup.send(f"Team {str(team_number)} 's next match is in **{int(timeTillMatch)} minutes** (QM{nextMatch[10:]})")
            await interaction.followup.send(embed = my_embed)

        ######
        #ELIMS
        ######

        else:
            print(f"elims found: {nextMatch}")

            for i in exactTeamInfo:
                if(str(i["key"])[8:] == str(nextMatch[8:])):
                    timeTillMatch = (i["predicted_time"] - time.time())/60
                    blueAlliance = str(i["alliances"]["blue"]["team_keys"]).translate({ord(i): None for i in "frc'[]"})
                    redAlliance = str(i["alliances"]["red"]["team_keys"]).translate({ord(i): None for i in "frc'[]"})
                    

                    if str(team_number) in blueAlliance:
                        blueAlliance = blueAlliance.replace(f"{str(team_number)}", f"**{str(team_number)}**")
                        embed_color= 40151
                    else:
                        redAlliance = redAlliance.replace(f"{str(team_number)}", f"**{str(team_number)}**")
                        embed_color=15539236


            if int(timeTillMatch) < 0:
                my_embed = discord.Embed(title=f"Team {team_number}'s next match started {abs(int(timeTillMatch))} minutes ago", description=f"next match: **{nextMatch[8:]}**", color=int(embed_color))
            else:
                my_embed = discord.Embed(title=f"Team {team_number}'s next match is in {int(timeTillMatch)} minutes", description=f"next match: **{nextMatch[8:]}**", color=int(embed_color))
            my_embed.add_field(name="Red alliance", value=redAlliance)
            my_embed.add_field(name="Blue alliance", value=blueAlliance)
            my_embed.set_thumbnail(url='https://frcavatars.herokuapp.com/get_image?team='+str(team_number))


            #await interaction.followup.send(f"Team {str(team_number)} 's next match is in **{int(timeTillMatch)} minutes** (QM{nextMatch[10:]})")
            await interaction.followup.send(embed = my_embed)

    ######
    #ERROR
    ######

    except Exception as e: 
        print(e)
        print(f"LOGGING: lol {interaction.user} really tried looking up {team_number} but they dont have any matches")
        await interaction.followup.send(f"Team {team_number} is not playing this weekend!")

client.run('')
