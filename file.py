#!/usr/bin/python3

import discord
import asyncio
import config as cfg
import urllib.request

print("Connecting")
client = discord.Client()

downloadfolder = "/home/steam/testdl"

@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("----")

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
                    print("Should download now")
                    print("url:", attachment['url'])
                    urllib.request.urlretrieve(attachment['url'], downloadfolder + "/" + attachment['filename'])

def is_me(m):
    return m.author == client.user

client.run(cfg.token)
