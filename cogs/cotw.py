
#import requests
#import discord.ext
import random
import logging
#rom PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageColor
#import io
import mysql.connector
import re
#from discord.ext import commands
from interactions import *

from interactions.ext.wait_for import wait_for, setup
from interactions.ext.tasks import create_task, IntervalTrigger
import interactions
import asyncio
from datetime import datetime, timedelta
host = "localhost"
triggered = False
#host = "212.111.42.251"
logger = logging.getLogger("bot")


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
ALLOWED_LINKS= ("xbox", "gifyourgame","youtube", "youtu","twitter",)
ALLOWED_NON_WWW = ("youtu", "medal", "cdn.discordapp")


class COTW(interactions.Extension):
    def __init__(self, bot):
        self.bot: interactions.Client = bot
        self.channel = 941073900173938718   
    async def getLeaderBoard(self, ctx=None):
        cur = connect(host)
        cur.execute("SELECT * FROM submissions")
        records = cur.fetchall()
        if len(records) == 0:
            if ctx is not None:
                await ctx.send("No one has submitted anything")
            else:
                print("No one has submitted anything")
            return

        def takeScore(elem):
            
            return elem[2]
        guild = interactions.Guild(**await self.bot._http.get_guild(GUILD_ID))
        embed = interactions.Embed(title="Clip leaderboard")
        counter=1
        i = 0
        for record in records:
            msgId = record[1]
            try:
                msg = interactions.Message(**await self.bot._http.get_message(self.channel, msgId))
            except:
                continue
            reactions = msg.reactions
            up = reactions[0].count - 1
            score = up
            records[i] = list(records[i])
            records[i].append(score)
            i+=1
        for record in sorted(records, key=takeScore, reverse=True):
            member =  interactions.User(**await self.bot._http.get_user(record[0]))
            if counter == 1:
                place = ":first_place:"
            elif counter == 2:
                place = ":second_place:"
            elif counter == 3:
                place = ":third_place:"
            elif counter == 11:
                break
            else:
                place= "#" + str(counter)
            score = record[2]
            id = record[1]
            mention = member.mention if member is not None else "Deleted user"
            name = member.username if member is not None else "Deleted user"
            embed.add_field(name=f"{place} {name}", value=f"{mention}, Link: https://discord.com/channels/917891087006334976/{str(self.channel)}/{id}\nScore `{score}`\n", inline=False)
            counter+=1        

        return embed
    @interactions.extension_command(name="leaderboard", description="Shows the leaderboard for this week", scope=GUILD_ID)
    async def leaderboard_command(self, ctx):
        await ctx.defer()
        embed = await self.getLeaderBoard(ctx)
        await ctx.send(embeds=embed)

    @interactions.extension_command(name="restartweek", description="manually restart week", scope=GUILD_ID,default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    async def restart_command(self,ctx):

        date = datetime.utcnow()
        logger.debug(f"Restarting week at from command at {date}")
        cur = connect(host)
        cur.execute("DELETE FROM submissions")

        channel = interactions.Channel(**await self.bot._http.get_channel(self.channel), _client=self.bot._http)
        embed= interactions.Embed(title="All submissions reset!", description="Every monday at midnight, submissions reset for the next video. Do /submissions to see your submissions")
        await channel.send(embeds=embed)
        modChannel = interactions.Channel(**await self.bot._http.get_channel(992955793697689690), _client=self.bot._http)
        embed = await self.getLeaderBoard()
        await modChannel.send(embeds=embed)
        con.commit()
        await ctx.send("Done. Week manually restarted")
        cur.close()
        con.close()

    @interactions.extension_command(name="submitafter", description="submits all posts after a certain point", scope=GUILD_ID, default_member_permissions=interactions.Permissions.ADMINISTRATOR, options = [interactions.Option(name="message", description="The message to submit after", type=interactions.OptionType.INTEGER)])
    async def submitAfter(self, ctx: interactions.CommandContext, id: interactions.Message):
        channel = interactions.Channel(**await self.bot._http.get_channel(self.channel), _client=self.bot._http)
        cur = connect(host)
        messages = await channel.history(start_at=id)
        status = ""
        for message in messages:
            asyncio.sleep(0.1)
            message = interactions.Message(**await self.bot._http.get_message(channel_id=self.channel,message_id= ctx.target.id), _client=self.bot._http)

            cur.execute("SELECT * FROM submissions WHERE msgId = %s", (int(message.id),))
            records = cur.fetchone()
            logger.debug(records)
            if records is not None:
                await ctx.send("That person's clips has already been submitted!", ephemeral=True)
                return
            authorId = message.author.id
            cur.execute("INSERT INTO submissions VALUES (%s,%s)", (int(authorId), int(message.id)))
            await message.create_reaction("👍", )

            status+=f"Resubmitted {message.author.username}'s clip! https://discord.com/channels/917891087006334976/{str(self.channel)}/{message.id}\n"
            if message.thread is None: await message.create_thread(name="Clip comments", invitable=True)
            con.commit()
        cur.close()
        con.close()
    @interactions.extension_message_command(name="Submit", type=interactions.ApplicationCommandType.MESSAGE, scope=GUILD_ID,default_member_permissions=interactions.Permissions.ADMINISTRATOR)
    async def submit_command(self, ctx: interactions.CommandContext):
        cur = connect(host)
        message = interactions.Message(**await self.bot._http.get_message(channel_id=self.channel,message_id= ctx.target.id), _client=self.bot._http)

        cur.execute("SELECT * FROM submissions WHERE msgId = %s", (int(message.id),))
        records = cur.fetchone()
        logger.debug(records)
        if records is not None:
            await ctx.send("That person's clips has already been submitted!", ephemeral=True)
            return
        authorId = message.author.id
        cur.execute("INSERT INTO submissions VALUES (%s,%s)", (int(authorId), int(message.id)))

        await message.create_reaction("👍", )
        await message.create_reaction("👎", )

        await ctx.send(f"Resubmitted {message.author.username}'s clip!\nhttps://discord.com/channels/917891087006334976/{str(self.channel)}/{message.id}", ephemeral=True)
        if message.thread is None: await message.create_thread(name="Clip comments", invitable=True)
        con.commit()
        cur.close()
        con.close()

    @interactions.extension_command(name="submissions", description="lists your submissions")
    async def sumbmissionCommand(self, ctx):
            cur = connect(host)
            cur.execute("SELECT * FROM submissions WHERE memberId = %s", (int(ctx.author.id),))
            records = cur.fetchall()
            con.close()
            logger.debug(records)
            if len(records) == 0: 
                await ctx.send("You have no submissions this week!")
                return


            link1 = "https://discord.com/channels/917891087006334976/" + str(self.channel) + "/"+ str(records[0][1])
            embed = interactions.Embed(title="Submitted clips", description="Clips you have submitted!")
            embed.add_field(name="Clip 1", value=link1)
            
            link2 = "No second clip submitted"
            if len(records) > 1: link2 = "https://discord.com/channels/917891087006334976/" + str(self.channel) + "/" + str(records[1][1])
            

            
            embed.add_field(name="Clip 2", value=link2)
            error = await ctx.send(embeds=embed) 
                
    @interactions.extension_listener()
    async def on_start(self):
        cur =connect(host)
        now = datetime.utcnow()
        future = datetime(now.year, now.month, now.day,0,0,0,0) + timedelta(days=1)
        logger.debug(f"waiting for {(future-now).seconds} seconds")
        await asyncio.sleep((future-now).seconds+2)
        logger.debug(datetime.utcnow().strftime("%a").lower())
        self.clearDataBase.start(self)
        
        if datetime.utcnow().strftime("%a").lower() == "mon":
            date = datetime.utcnow()
            logger.debug(f"Restarting week at {date}")
            cur.execute("DELETE FROM submissions")
            modChannel = interactions.Channel(**await self.bot._http.get_channel(992955793697689690), _client=self.bot._http)
            embed = await self.getLeaderBoard(None)
            await modChannel.send(embeds=embed)
            channel = interactions.Channel(**await self.bot._http.get_channel(self.channel), _client=self.bot._http)
            embed= interactions.Embed(title="All submissions reset!", description="Every week submissions reset for the next video. Do /submissionights to see your submissions")
            await channel.send(embeds=embed)


        con.commit()
        cur.close()
        con.close()

    @interactions.extension_listener()
    async def on_message_delete(self, msg):
        if msg.channel_id == self.channel:
            cur = connect(host)
            
            cur.execute("DELETE FROM submissions WHERE msgId = %s",(int(msg.id),))
            print("deleted")
            cur.close()
            con.commit()
            con.close()


    @interactions.extension_listener()
    async def on_message_reaction_add(self,msg: interactions.MessageReaction):
        
        if msg.emoji.name == "👍" and msg.user_id != 966807823486963713:
            cur = connect(host)
            cur.execute("SELECT * FROM submissions WHERE msgId = %s", (int(msg.message_id),))
            record = cur.fetchone()
            if record is None or record[0] != msg.user_id: return
            
            cur.close()
            con.close()
            submission = interactions.Message(**await self.bot._http.get_message(channel_id=self.channel,message_id= msg.message_id, ), _client=self.bot._http)
            user = interactions.User(**await self.bot._http.get_user(user_id=msg.user_id, ))
            await submission.remove_reaction_from(emoji="👍",user=user)
            channel = interactions.Channel(**await self.bot._http.get_channel(self.channel), _client=self.bot._http)
            error = await channel.send("We appreciate your self-pride but you cannot upvote your own clip!")
            await asyncio.sleep(3)
            await error.delete()
            

    @interactions.extension_listener()
    async def on_message_create(self, msg):
        upload = False
        isLink = False
        allowed = False
        if msg.author.id == self.bot.me.id: return

        guild = interactions.Guild(**await self.bot._http.get_guild(GUILD_ID), _client=self.bot._http)
        channel = interactions.Channel(**await self.bot._http.get_channel(self.channel), _client=self.bot._http)
        
        if msg.channel_id == channel.id:
            cur = connect(host)
            msgList = msg.content.split()
            attachment = msg.attachments if msg.attachments is not None else []
            
            if len(attachment) ==1:
                upload = True

                
            elif len(attachment) > 1 :
                await msg.delete()
                error = await channel.send("You cannot upload more than clip at once! Upload separately", )
                await asyncio.sleep(3)
                await error.delete()

            if not upload:
                
                counter = 0
                for word in msgList:
                    word=word.strip()
                    if word.startswith("https://"):
                        isLink = True
                        link = word
                        counter+=1

                    if counter > 1: 
                        await msg.delete()
                        error = await channel.send("You cannot send more than two clips at once! Send them separately")
                        await asyncio.sleep(3)
                        await error.delete()
                        return
                
                    for handle in ALLOWED_LINKS:
                        if word.startswith("https://medal") or word.startswith("https://youtu.be") or word.startswith("https://cdn.discordapp"):
                            allowed = True
                            break
                        if word.startswith("https://www." + handle):
                            allowed = True
                            break
            if not (isLink or upload) or (isLink and upload):
                member = interactions.Member(**await self.bot._http.get_member(guild_id=GUILD_ID, member_id=msg.author.id))
                roles = member.roles if member.roles is not None else []
                
                if 917892776438411375 in roles:
                    return

                await msg.delete()
                error = await channel.send("Only clips can be sent here one at a time.")
                await asyncio.sleep(5)
                await error.delete()
                return

            if (not allowed) and (not upload):
                await msg.delete()
                error = await channel.send("This doesn't seem to be a clip link. If you feel this is in error contact a mod! Or try uploading your clip to a more popular site")
                await asyncio.sleep(5)
                await error.delete()
                return 

            cur.execute("SELECT * FROM submissions WHERE memberId = %s", (int(msg.author.id),))
            records = cur.fetchall()
            logger.debug(len(records))
            if len(records) >= 2:
                await msg.delete()
                embed = interactions.Embed(title="You have already sent 2 clips this week!", description="These are the clips you already submitted, go back and delete one to post more")
                
                link1 = f"https://discord.com/channels/917891087006334976/{str(self.channel)}/"
                link2 = f"https://discord.com/channels/917891087006334976/{str(self.channel)}/" 
                link1+=str(records[0][1])
                link2+=str(records[1][1])

                embed.add_field(name="Clip 1", value=link1)
                embed.add_field(name="Clip 2", value=link2)
                error = await channel.send(embeds=embed)

                await asyncio.sleep(10)
                await error.delete()
                return
            logger.debug(int(msg.id))
            cur.execute("INSERT INTO submissions VALUES (%s,%s)", (int(msg.author.id), int(msg.id)))
            con.commit()
            print((int(msg.author.id), int(msg.id)))
            await msg.create_reaction("👍")
            await msg.create_reaction("👎")
            await msg.create_thread(name="Clip comments", invitable=True)

            
            con.close()


    @create_task(IntervalTrigger(delay=3600*24))
    async def clearDataBase(self):
        date = datetime.utcnow()
        logger.debug(f"triggered at {date}")
        print(datetime.utcnow().strftime("%a").lower())
        if datetime.utcnow().strftime("%a").lower() == "mon" and not triggered:
            date = datetime.utcnow()
            try:
                modChannel = interactions.Channel(**await self.bot._http.get_channel(992955793697689690), _client=self.bot._http)
                embed = await self.getLeaderBoard()
                await modChannel.send(embeds=embed)
            except Excpetion as e:
                modChannel.send(f"Error trying to send leaderboard: \n\n\"{e}\"")
            logger.debug(f"Restarting week at {date}")
            cur = connect(host)
            cur.execute("DELETE FROM submissions")
            con.commit()
            channel = interactions.Channel(**await self.bot._http.get_channel(self.channel), _client=self.bot._http)
            embed= interactions.Embed(title="All submissions reset!", description="Every monday at midnight, submissions reset for the next video. Do /submissions to see your submissions")
            await channel.send(embeds=embed)
            
            

            cur.close()
            con.close()


def setup(bot):
    COTW(bot)
