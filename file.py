#!/usr/bin/python3

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
    server = client.get_server(cfg.serverid)
    channel = server.get_channel(cfg.channelid)

@client.event
async def on_message(message):
    print("content", message.content)
    print("mentions", message.mentions)
    for user in message.mentions:
        print("id {}, name {}".format(user.id, user.name))

    if client.user in message.mentions:
        print("Ping!")
        attachments = len(message.attachments)
        print("Attachment count:", attachments)
        if attachments > 0:
            for attachment in message.attachments:
                print("Filename:", attachment['filename'])
                ext = attachment['filename'][-3:]
                print("Ext:", ext)
                if ext == "pbo":
                    print("Found a PBO")
                    print("Checking if exists")
                    outfile = downloadfolder + "/" + attachment['filename']
                    if os.path.isfile(outfile):
                        print("{} exists".format(outfile))
                        await client.send_message(message.channel, "File {} exists already!".format(attachment['filename']))
                        return
                    print("Should download now")
                    print("url:", attachment['url'])
                    #r = urllib.request
                    #r.add_header("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0")
                    #r.urlretrieve(attachment['url'], downloadfolder + "/" + attachment['filename'])
                    ret = os.system("wget {} -O {}".format(attachment['url'], outfile))
                    if ret == 0:
                        await client.send_message(message.channel, "Uploaded")
                    else:
                        await client.send_message(message.channel, "Error. Request manual upload.")

def is_me(m):
    return m.author == client.user

client.run(cfg.TOKEN)
