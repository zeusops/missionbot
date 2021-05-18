#!/usr/bin/env python3
import os
import pathlib
import subprocess
import traceback

from discord.ext import commands
from discord import ChannelType

import config as cfg


class Bot(commands.Bot):
    downloadfolder = pathlib.Path(f'{os.environ["HOME"]}/link/mpmissions')

    def __init__(self, *argv, **argc):
        super().__init__(*argv, **argc)
        self.gehock = None
        #self.add_listener(self.on_ready)
        #self.add_listener(self.on_message)

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("----")
        #server = client.get_guild(cfg.serverid)
        #channel = client.get_channel(cfg.channelid)
        self.owner = await self.fetch_user(150625032656125952)
        print("owner", self.owner)
        self.owner_dm = self.owner.dm_channel

    async def on_message(self, message):
        if self.is_me(message):
            return
        if (message.channel.id not in cfg.CHANNEL_IDS
                and not (message.channel.type == ChannelType.private
                         and message.author == self.owner)):
            print(f"#{message.channel}: <{message.author}> {message.content}")
            return

        if message.attachments:
            for attachment in message.attachments:
                ext = attachment.filename.split('.')[-1]
                if ext != 'pbo':
                    print(f"{attachment.filename} is not a pbo")
                    await message.channel.send("Not a pbo, not uploading")
                    return
                outfile = self.downloadfolder / attachment.filename
                if os.path.isfile(outfile):
                    print(f"{outfile} exists")
                    await message.channel.send(f"File {attachment.filename} already exists!")
                    return
                print("Should save now")
                #await message.channel.send(f"{gehock.mention} pls upload")
                if await attachment.save(outfile) != attachment.size:
                    await message.channel.send("Error. Request manual upload or try again.")
                    return
                await message.channel.send("Uploaded")
                try:
                    info=subprocess.check_output(["./pboinfo.py", outfile]).decode('utf-8')
                except Exception as e:
                    traceback.print_exc()
                    await message.channel.send("Failed to get PBO info")
                else:
                    await message.channel.send(info)

    def is_me(self, m):
        return m.author == self.user

if __name__ == "__main__":

    print("Connecting")
    bot = Bot('.')

    bot.run(cfg.TOKEN)
