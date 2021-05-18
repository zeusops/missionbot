#!/usr/bin/env python3
import os
import pathlib
import subprocess
import traceback

from discord.ext import commands
from discord import ChannelType

import config as cfg


def detect_platform():
    import sys
    if sys.platform in ["Windows, cygwin"]:
        return "windows"
    elif sys.platform == "linux":
        import platform
        if "Microsoft" in platform.release():
            return "wsl"
        else:
            return "linux"


class Bot(commands.Bot):
    def __init__(self, *argv, **argc):
        super().__init__(*argv, **argc)
        self.gehock = None

        platform = detect_platform()
        home = os.environ['HOME']
        if platform == "windows":
            missionpath = "C:/server/link/mpmissions"
        elif platform == "wsl":
            missionpath = "/mnt/c/server/link/mpmissions"
        else:
            missionpath = f"{home}/link/mpmissions"

        self.downloadfolder = pathlib.Path(missionpath)

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("----")
        # server = client.get_guild(cfg.serverid)
        # channel = client.get_channel(cfg.channelid)
        self.owner = await self.fetch_user(150625032656125952)
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
                    await message.channel.send(f"File {attachment.filename} "
                                               "already exists!")
                    return
                # await message.channel.send(f"{gehock.mention} pls upload")
                if await attachment.save(outfile) != attachment.size:
                    await message.channel.send("Error. Request manual upload "
                                               "or try again.")
                    return
                await message.channel.send("Uploaded")
                try:
                    info = subprocess.check_output(["./pboinfo.py",
                                                    outfile]).decode('utf-8')
                except Exception:
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
