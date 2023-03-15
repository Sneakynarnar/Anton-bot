
#import requests

#import random
#from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageColor
#import io
import mysql.connector
#import re
import cfscrape
from fake_useragent import UserAgent
import datetime
from datetime import datetime, timedelta
from interactions import *
from interactions.ext.wait_for import wait_for, setup
import interactions
import json
from interactions.api.models.message import Emoji
import asyncio
import cloudscraper
host = "localhost"
rankMap = {"Unranked": 0, "Bronze": 1, "Silver": 2, "Gold": 3, "Platinum": 4, "Diamond": 5, "Champion": 6, "Grand": 7, "Supersonic": 8}
host = "212.111.42.251"
def connect(host):
    global con
    con = mysql.connector.connect(
        host=host,
        user="sneaky",
        passwd="Dominus7206!",
        database="AntonServer",
    )
    cur = con.cursor(buffered=True)
    return cur

GUILD_ID = 917891087006334976
MODS = []
RANKED_ROLES = [921350819733995520,921350981994827796,921351026852892702,921351068514930699,921351115692445716,921351235263672380,921351174618234891,921351276816637963]

class Applications(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.colour = 0x0390fc
        self.bot_url = "https://cdn.discordapp.com/avatars/966807823486963713/f0d24c78a0bd0475b932911"

    def formatSeconds(self, seconds):
        fmt = ""
        days = int(seconds // (24 * 60 * 60))
        daysRem = seconds % (24 * 60 * 60)

        hours = int(daysRem // (60 * 60))
        hoursRem = daysRem % (60 * 60)

        minutes = int(hoursRem // 60)
        minutesRem = hours % 60

        seconds = int(minutesRem)
        if days != 0: fmt += f"{days} days,"
        if hours != 0: fmt += f" {hours} hours,"
        if minutes != 0: fmt += f" {minutes} minutes"
        fmt += f" and {seconds} seconds"
        return fmt

        
    @interactions.extension_command(name="srm", description="u know what it does nana", scope=GUILD_ID)
    async def srm(self, ctx):
        
        channel = interactions.Channel(**await self.bot._http.get_channel(921350783071584256), _client=self.bot._http)
        await channel.send(
            content="Click this for the bot to give you your rank, note that you could still be moved down if you are found to be not playing at your division in 2/4/6 mans.\
 **This data is stored, and if you are found to enter an account that does not belong to you, you WILL be banned.**", 
                components=[interactions.Button(style=interactions.ButtonStyle.SUCCESS, custom_id="autoranks", label="Give me my ranked role")])  
    
    @interactions.extension_modal("autorank")
    async def rank_response(self, ctx, response):
        cur = connect(host)
        scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'android',
        'desktop': False
        })
        res = scraper.get("https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/" + response)
        print(res.text)
        try:
            data = json.loads(res.text)
        except:
            await ctx.send("There was a problem accessing the tracker api, please try again later. Contact admins if this keeps happening.", ephemeral=True)
        if "errors" in data:
            await ctx.send("There was a problem finding the data for this account (it probably doesn't exist), if you feel this was in error contact Sneakynarnar#7573")
            
        else:
            topRank = "Unranked"
            for segment in data["data"]["segments"]:
                if segment["type"] == "overview":
                    continue
                else:
                    realRank = segment["stats"]["tier"]["metadata"]["name"]
                    if realRank == None: realRank = "Unranked"
                    rankList = realRank.split()
                    rank = rankList[0]
                    if rankMap[topRank] < rankMap[rank]:
                        topRank = rank
                    
            topRank = topRank.lower()
        if topRank == "unranked":
            await ctx.send("It seems you aren't currently ranked in any gamemodes, please play your placement matches and try again", ephemeral=True)                          
        elif topRank == "bronze":
            role = await ctx.guild.get_role(921350819733995520)
        elif topRank == "silver":
            role = await ctx.guild.get_role(921350981994827796)
        elif topRank == "gold":
            role = await ctx.guild.get_role(921351026852892702)
        elif topRank == "platinum":
            role = await ctx.guild.get_role(921351068514930699)
        elif topRank == "diamond":
            role = await ctx.guild.get_role(921351115692445716)
        elif topRank == "champion":
            role = await ctx.guild.get_role(921351174618234891)
        elif topRank == "grand":
            role = await ctx.guild.get_role(921351235263672380)
        elif topRank == "supersonic legend":             
            role = await ctx.guild.get_role(921351276816637963)           
    
        if role.id in RANKED_ROLES:
            for rankrole in ctx.author.roles:
                if rankrole in RANKED_ROLES:
                    await ctx.author.remove_role(rankrole, ctx.guild.id)

        await ctx.author.add_role(role, ctx.guild.id)
        cur.execute("INSERT INTO epicUserNames VALUES (%s,%s)", (int(ctx.author.id), response))
        await ctx.send(content=f"I have given you the {role.name} role! This is your current rank, if you for some reason need to change your epic name, open a support ticket", ephemeral=True)
        con.commit()
        con.close() 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
    @interactions.extension_modal("modapp")
    async def modal_response(self, ctx, response):
        cur = connect(host)
        print(response)
        channel = interactions.Channel(**await self.bot._http.get_channel(987752824223981619), _client=self.bot._http)
        embed = interactions.Embed(title=f"{ctx.author.user.username}'s application",description=f"{response}\n\n{ctx.author.mention}")


        actionrow = interactions.ActionRow(components=[
            interactions.Button(style=ButtonStyle.SUCCESS, label="Accept for interview", custom_id=f"accept{ctx.author.id}"),
            interactions.Button(style=ButtonStyle.DANGER, label="Decline", custom_id=f"decline{ctx.author.id}")])
        cur.execute("SELECT * FROM applications WHERE authorID=%s", (int(ctx.author.id),))
        if cur.fetchone() is not None:
            await ctx.send("You have already applied for mod before! You can't apply again.", ephemeral=True)
            return
        application = await channel.send(embeds=embed, components=[actionrow])

        cur.execute("INSERT INTO applications VALUES (%s)", (int(ctx.author.id),))
        await ctx.send("Your response has been submitted!", ephemeral=True)
        con.commit()
        con.close()
    @interactions.extension_listener()
    async def on_component(self, ctx):
        await ctx.get_guild()
        guild = ctx.guild
        cur = connect(host)
        print(ctx.custom_id)
        role = None
        if ctx.custom_id.startswith("accept"):
            await ctx.defer(edit_origin=True)
            memberId = int(ctx.custom_id[6:])

            user = await guild.get_member(memberId)

            # await user.create_dm()
            await user.send(
                "Good news! We liked your application and would like to talk to you more about being a mod! Someone from the moderation team will contact you shortly!")
            await ctx.edit(content=f"Accepted for interview by {ctx.author.mention}!", components=None)
            con.commit()

        elif ctx.custom_id.startswith("decline"):
            await ctx.defer(edit_origin=True)
            memberId = int(ctx.custom_id[7:])

            user = await guild.get_member(memberId)
            await user.send(
                "We appreciate you wanting to help out in the server! But we have decided you are not what we are looking for in a mod right now, thank you for applying.\n\nSincerely - The Mod Team :)" )
            await ctx.edit(content=f"Declined by {ctx.author.mention}!", components=None)
            con.commit()
        elif ctx.custom_id.startswith("application"):
            now = datetime.utcnow()
            now = now.replace(tzinfo=None)
            future = ctx.author.joined_at + timedelta(weeks=4)
            future = future.replace(tzinfo=None)
            t = future - now
            print(f"now: {now}")
            print(f"then: {ctx.author.joined_at}")
            print(f"future {future}")
            print(t.total_seconds())
            tform = self.formatSeconds(t.total_seconds())
            if t.total_seconds() > 0:

                await ctx.send(f"Hey! Sorry you cannot apply until you have been in the server for at least 4 weeks.\n\nYou can apply in {tform}.", ephemeral=True)
                return
            modal = interactions.Modal(title="Mod Application", custom_id="modapp",
                    components=[interactions.TextInput(style=interactions.TextStyleType.PARAGRAPH, custom_id="modappresponse",
                    label="Why should you be mod?",
                    min_lenth=500, max_length=2000)])
            await ctx.popup(modal)
        elif ctx.custom_id == "autoranks":
            cur = connect(host)
            cur.execute("SELECT epicId FROM epicUserNames WHERE discordId = %s", (int(ctx.author.id),))
            epicName = cur.fetchone()
            if epicName is not None:
                epicName = epicName[0]
                ua = UserAgent()
                scraper = cloudscraper.create_scraper(browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
                })
                res = scraper.get("https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/", headers={"useragent": f"{ua.random}"})
                print(res.text)
                try:
                    data = json.loads(res.text)
                except:
                    await ctx.send("There was a problem accessing the tracker api, please try again later. Contact admins if this keeps happening.", ephemeral=True)
                if "errors" in data:
                    await ctx.send("There was a problem finding the data for this account (it probably doesn't exist), if you feel this was in error contact Sneakynarnar#7573", ephemeral=True)
                    
                else:
                    topRank = "Unranked"
                    for segment in data["data"]["segments"]:
                        if segment["type"] == "overview":
                            continue
                        else:
                            realRank = segment["stats"]["tier"]["metadata"]["name"]
                            if realRank == None: realRank = "Unranked"
                            rankList = realRank.split()
                            rank = rankList[0]
                            if rankMap[topRank] < rankMap[rank]:
                                topRank = rank
                            
                    topRank = topRank.lower()
                if topRank == "unranked":
                    await ctx.send("It seems you aren't currently ranked in any gamemodes, please play your placement matches and try again", ephemeral=True)                          
                elif topRank == "bronze":
                    role = await ctx.guild.get_role(921350819733995520)
                elif topRank == "silver":
                    role = await ctx.guild.get_role(921350981994827796)
                elif topRank == "gold":
                    role = await ctx.guild.get_role(921351026852892702)
                elif topRank == "platinum":
                    role = await ctx.guild.get_role(921351068514930699)
                elif topRank == "diamond":
                    role = await ctx.guild.get_role(921351115692445716)
                elif topRank == "champion":
                    role = await ctx.guild.get_role(921351174618234891)
                elif topRank == "grand":
                    role = await ctx.guild.get_role(921351235263672380)
                elif topRank == "supersonic":             
                    role = await ctx.guild.get_role(921351276816637963)           
            
                if role.id in RANKED_ROLES:
                    for rankrole in ctx.author.roles:
                        if rankrole in RANKED_ROLES:
                            await ctx.author.remove_role(rankrole, ctx.guild.id)

                await ctx.author.add_role(role, ctx.guild.id)
                await ctx.send(content=f"I have given you the {role.name} role! This is your current rank on your connected account \"{epicName}\", if you for some reason need to change your epic name, open a support ticket", ephemeral=True)

                return
            modal = interactions.Modal(title="Enter your epic games Id", custom_id="autorank",
            components=[interactions.TextInput(style=interactions.TextStyleType.PARAGRAPH, custom_id="autoroleresponse",
            label="Enter your epic username",
            min_lenth=2, max_length=16)])
            await ctx.popup(modal)

        elif ctx.custom_id == "bronze":
            role = await ctx.guild.get_role(921350819733995520)
        elif ctx.custom_id == "silver":
            role = await ctx.guild.get_role(921350981994827796)
        elif ctx.custom_id == "gold":
            role = await ctx.guild.get_role(921351026852892702)
        elif ctx.custom_id == "plat":
            role = await ctx.guild.get_role(921351068514930699)
        elif ctx.custom_id == "diamond":
            role = await ctx.guild.get_role(921351115692445716)
        elif ctx.custom_id == "champ":
            role = await ctx.guild.get_role(921351174618234891)
        elif ctx.custom_id == "gc":
            role = await ctx.guild.get_role(921351235263672380)
        elif ctx.custom_id == "Announcement":
            role = await ctx.guild.get_role(1018645903860580412)
        elif ctx.custom_id == "4mans":
            role = await ctx.guild.get_role(1017569035279421500)
        elif ctx.custom_id == "2mans":
            role = await ctx.guild.get_role(1077293015464431626)
        elif ctx.custom_id == "6mans":
            role = await ctx.guild.get_role(1077293366896754738)
        elif ctx.custom_id == "uploads":
            role = await ctx.guild.get_role(1018646108198682634)
        elif ctx.custom_id == "EU":
            role = await ctx.guild.get_role(1063580354608365568)
        elif ctx.custom_id == "NA":
            role = await ctx.guild.get_role(1063580400221438003)
        elif ctx.custom_id == "OCE":
            role = await ctx.guild.get_role(1063580429468315698)

        else:
            return
        try:
            if role is None: return
            
            
            if role.id in ctx.author.roles:
                await ctx.author.remove_role(role, ctx.guild.id)
                await ctx.send(content=f"I have removed the {role.name} role!", ephemeral=True, )
            else:
                if (ctx.author.id == 617009307321368781 and role.id == 921351235263672380) or (ctx.author.id == 395787452331327490 and role.id == 921351235263672380):
                    await ctx.send("https://www.fiverr.com/astrix2/provide-professional-rocket-league-coaching", ephemeral=True)
                    return
                    
                if role.id in RANKED_ROLES:
                    for rankrole in ctx.author.roles:
                        if rankrole in RANKED_ROLES:
                            await ctx.send(content=f"You already have the another ranked role! To add a new one remove the other!", ephemeral=True)
                            return
                await ctx.author.add_role(role, ctx.guild.id)
                await ctx.send(content=f"I have given you the {role.name} role!", ephemeral=True, )
        except Exception as e:
            print(e)
        cur.close()
        con.close()


def setup(bot):
    Applications(bot)