

#import requests

#import random
#from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageColor
#import io
import mysql.connector
#import re

from interactions import *
from interactions.ext.wait_for import wait_for, setup
import interactions
from datetime import datetime
import asyncio
host = "localhost"
chatlog = []
RANKED_ROLES = [921350819733995520,921350981994827796,921351026852892702,921351068514930699,921351115692445716,921351235263672380,921351174618234891,921351276816637963]

#host = "212.111.42.251"
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

class Commands(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.colour = 0x0390fc
        self.bot_url ="https://cdn.discordapp.com/avatars/966807823486963713/f0d24c78a0bd0475b932911"
    @interactions.extension_listener()
    async def on_member_join(self, member):
        await member.add_role(968549819947831366)

    @interactions.extension_listener()
    async def on_message_create(self, message):
        if message.channel_id == 1020491263474151535:
            if message.author.id == self.bot.me.id: return
            rlqc = ["Nice shot!", "What a save!", "Nice one!", "Nice bump!", "Nice demo!","Nice shot!", "Great pass!",\
                "Great clear!", "Nice block!", "What a play!", "Thanks!", "No problem.", "Whew.", "Centering.",
                "In position.", "Incoming!", "All yours.", "Go for it!", "Defending...", "Take the shot!", "Wow!", \
                "Need boost!", "Close one!", "OMG!", "No way!", "Hxoly cow", "Siiick!", "Savage!", "Noooo!", \
                "$#@%!", "Whoops…", "Oops!", "Sorry!", "My fault.", "My bad...", "Calculated!", "Okay.", "gg", \
                 "That was fun!", "Everybody dance!", "Nice moves.", "Well played.", "One. More. Game", "Rematch!", \
                    "This is Rocket League!", "Get ready!", "Here. We. Go", "Nice cars.", "What a game!", "Faking!", \
                        "Bumping!", "On your left.", "On your right.", "Faking!", "Passing!", "I'll do my best."]

            if message.content not in rlqc:
                await message.delete()
            else:
                chatlog.append([message.author.id, message.content])
                counter=0
                qc = ""
                for msg in chatlog:
                    print(msg)
                    if msg[0] == message.author.id:
                        if qc == msg[1]:
                            counter+=1
                        else:
                            qc = msg[1]
                    if counter == 2:
                        guild = interactions.Guild(**await self.bot._http.get_guild(GUILD_ID), _client=self.bot._http)
                        member = await guild.get_member(message.author.id)
                        role = await guild.get_role(1020503795186274334, )
                        channel = interactions.Channel(**await self.bot._http.get_channel(message.channel_id),_client=self.bot._http)
                        await channel.send(f"{member.mention} Chat disabled for 3 seconds")
                        await member.add_role(role, guild_id=GUILD_ID)

                        await asyncio.sleep(3)
                        await member.remove_role(role,guild_id=GUILD_ID)
                        for i, msg in enumerate(chatlog):
                            if msg[0] == member.id:
                                del chatlog[i]
                            
                        break
                        

                

    @interactions.extension_listener()
    async def on_ready(self):
        print("Commands Cog loaded!")
        print(self.bot.guilds)

    @interactions.extension_command(name="invite", scope=GUILD_ID,description="Invite link to the server")
    async def invitecommand(self,ctx):
        await ctx.send("You can invite your friends to the server with this link, thanks in advance!: https://discord.gg/QzTjdzKhfm")

    @interactions.extension_command(name="removeroleall", scope=GUILD_ID, description="Gives everyone a role", default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    async def role_all_command(self, ctx):

        guild = await ctx.get_guild()
        members = await guild.get_all_members()
        for member in members:
            if member.user.bot: continue
            print(member.username)
            try:
                for rankrole in member.roles:
                    if rankrole in RANKED_ROLES:
                        print(member.username, rankrole.name)
                        await member.remove_role(rankrole, guild.id)
            except Exception as e:
                print(e)
        await ctx.send("Done.")
    @interactions.extension_command(name="version", scope=GUILD_ID,description="Version of the bot")
    async def versionCommand(self, ctx):
        embed= interactions.Embed(title="Anton bot", color=self.colour)
        embed.add_field(name="Version", value="V1.39")
        dev = interactions.User(**await self.bot._http.get_user(339866237922181121))
        name = dev.username +"#"+ dev.discriminator
        embed.add_field(name="Bot developer",value=f"{name}", inline=False)

        embed.set_thumbnail(url=self.bot_url)
        await ctx.send(embeds=embed)

    @interactions.extension_command(name="clearsubmissions", scope=GUILD_ID, description="clears submissions", default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    async def clear_database(self, ctx):
        if ctx.author.id != 339866237922181121: return
        cur = connect(host)
        cur.execute("DELETE FROM submissions;")
        await ctx.send("Deleted all submissions, resetting")
        con.commit()
        cur.close()
        con.close()
    @interactions.extension_command(name="makeannouncement", default_member_permissions=interactions.Permissions.ADMINISTRATOR, description="Make a *fancy* announcement", scope=GUILD_ID, options = [
                                                        interactions.Option(name="title",description="The title of the announcement", type=3, required=True ), 
                                                        interactions.Option(name="channel", description="The channel you want to send the announcemnt in", type=7,required=True),
                                                        interactions.Option(name="showauthor", description="Show who sent this announcemnt", required=False,type=5,),
                                                        interactions.Option(name="mentions", description="Mentions will be before the embed", required=False, type=3,),
                                                        interactions.Option(name="skipdesc", description="This will skip the description and go straight to adding a field", type=5,required=False)
                                                        ])
    async def makeAnnouncements(self, ctx: interactions.CommandContext, title: str, channel, showauthor=None, mentions=None, includeservericon=None, skipdesc=None):
        showauthor = False if showauthor is None else showauthor
        includeservericon = False if includeservericon is None else includeservericon
        skipdesc = False if skipdesc is None else skipdesc    
        async def waitForMessage():
            def check(m):
                print(m.content)
                return m.author.id == ctx.author.id and m.channel_id == ctx.channel.id

            try:
                message = await wait_for(self.bot,name='on_message_create', timeout=600, check=check)
            except asyncio.TimeoutError:
                await ctx.channel.send("Timed out.")
            return message

        await ctx.defer()
        await ctx.get_channel()
        await ctx.get_guild()
        if not skipdesc:
            delmessage = await ctx.channel.send(
                "Send a message of the content of this announcement! (You can use any text modifications such as **BOLD** and __underline__)")
            message = await waitForMessage()
            description = message.content
            
            
        else:
            description = ""
        embed = interactions.Embed(title=title, description=description)
        embed.color = 0x8018f0
        if showauthor:
            embed.set_footer(text=f"This announcement was made by {ctx.author.user.username}",
                             icon_url=ctx.author.user.avatar_url, )

        sendButton = interactions.Button(style=ButtonStyle.SUCCESS, label="Looks good! Send it!", custom_id="confirm")
        fieldButton = interactions.Button(style=ButtonStyle.PRIMARY, label="Add a new field", custom_id="field")
        delButton = interactions.Button(style=ButtonStyle.DANGER, label="Delete last field", custom_id="del", )
        cancelButton = interactions.Button(style=ButtonStyle.DANGER, label="Cancel", custom_id="cancel")
        row = [sendButton, fieldButton, delButton, cancelButton]
        actionrow = interactions.ActionRow(components=row)
        if not skipdesc:

            await message.delete()
            await delmessage.delete()

        embedMessage = await ctx.send(content="This is a preview of the message that will be sent in the channel.",
                                          embeds=embed, components=[actionrow])

        def check(button_ctx):
            print(button_ctx.author.id == ctx.author.id)
            return button_ctx.author.id == ctx.author.id
        
        buttonCtx: ComponentContext = await self.bot.wait_for_component(components=row,check=check)
        confirmed = False
        while not confirmed:
            await buttonCtx.defer(edit_origin=True)

            if not skipdesc:
                if buttonCtx.custom_id == "confirm" and buttonCtx.author.id == ctx.author.id:
                    await channel.send(content=mentions, embeds=embed)
                    await buttonCtx.edit(embeds=None, content="Sent!", components=None)
                    confirmed = True
                    return
                elif buttonCtx.custom_id == "cancel" and buttonCtx.author == ctx.author:
                    await buttonCtx.edit(embeds=None, content="Cancelled", components=None)
                    return
                elif buttonCtx.custom_id == "field" and buttonCtx.author.id == ctx.author.id :
                    delMessage = await ctx.channel.send("What is the title of the field?")
                    message = await waitForMessage()
                    name = message.content
                    await message.delete()
                    await asyncio.sleep(0.1)
                    await delMessage.delete()
                    delMessage = await ctx.channel.send("What is the content of the field?")
                    message = await waitForMessage()
                    value = message.content
                    await message.delete()
                    await asyncio.sleep(0.1)
                    await delMessage.delete()
                    embed.add_field(name=name, value=value, inline=False)

                    await buttonCtx.edit(embeds=embed)
                elif buttonCtx.custom_id == "del" and buttonCtx.author.id == ctx.author.id:
                    index = len(embed.fields) -1
                    embed.remove_field(index)
                    await buttonCtx.edit(embeds=embed)
                    
            else:

                delMessage = await ctx.channel.send("What is the title of the field?")
                message = await waitForMessage()
                name = message.content
                await message.delete()
                await asyncio.sleep(0.1)
                await delMessage.delete()
                delMessage = await ctx.channel.send("What is the content of the field?")
                message = await waitForMessage()
                value = message.content
                await message.delete()
                await asyncio.sleep(0.1)
                await delMessage.delete()
                embed.add_field(name=name, value=value)

                embedMessage = await ctx.send(content="This is a preview of the message that will be sent in the channel.",embeds=embed, components=[actionrow], )
                skipdesc = False


            buttonCtx: ComponentContext = await self.bot.wait_for_component(components=row)
def setup(bot):
    Commands(bot)