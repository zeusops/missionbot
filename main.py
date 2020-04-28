#!/usr/bin/env python3
import discord  # pip install --user discord.py
import asyncio
import config as cfg
import urllib.request
import os
import os.path


print("Connecting")
client = discord.Client()

downloadfolder = "/home/steam/arma3/mpmissions"

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("----")
    #server = client.get_guild(cfg.serverid)
    channel = client.get_channel(cfg.channelid)
    #await client.send(channel, "no u")

@client.event
async def on_message(message):
    print("#{}: <{}> {}".format(message.channel, message.author, message.content))
    #if message.author == client.user:
    #    return
    for user in message.mentions:
        print("id {}, name {}".format(user.id, user.name))

    #if client.user in message.mentions:
    #    print("Ping!")
    attachments = len(message.attachments)
    if attachments > 0:
        print("Attachment count:", attachments)
        for attachment in message.attachments:
            print("Filename:", attachment.filename)
            ext = attachment.filename[-3:]
            print("Ext:", ext)
            if ext == "pbo":
                print("Found a PBO")
                print("Checking if exists")
                outfile = downloadfolder + "/" + attachment.filename
                if os.path.isfile(outfile):
                    print("{} exists".format(outfile))
                    await message.channel.send("File {} exists already!".format(attachment.filename))
                    return
                print("Should download now")
                print("url:", attachment.url)
                #r = urllib.request
                #r.add_header("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0")
                #r.urlretrieve(attachment.url, downloadfolder + "/" + attachment.filename)
                ret = os.system("wget {} -O {}".format(attachment.url, outfile))
                if ret == 0:
                    await message.channel.send("Uploaded")
                else:
                    await message.channel.send("Error. Request manual upload or try again.")

def is_me(m):
    return m.author == client.user

client.run(cfg.TOKEN)
