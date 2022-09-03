#!/usr/bin/env python3
import os
import pathlib
import platform
import shutil
import sys
import traceback

from discord import ChannelType
from discord.ext import commands
from discord.message import Message

import config as cfg
from pboinfo import get_info

CFG_VERSION = 1


def detect_platform():
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    if sys.platform == "linux":
        if "microsoft" in platform.release().lower():
            return "wsl"
        return "linux"
    raise ValueError(f"Unsupported platform {sys.platform}")


class Bot(commands.Bot):
    def __init__(self, *argv, **argc):
        super().__init__(*argv, **argc)
        self.owner = None

        platform = detect_platform()
        home = os.environ['HOME']
        if platform == "windows":
            missionpath = "C:/server/link/mpmissions"
        elif platform == "wsl":
            missionpath = "/mnt/c/server/link/mpmissions"
        else:
            missionpath = f"{home}/link/mpmissions"

        if cfg.CFG_VERSION != CFG_VERSION:
            raise ValueError(f"Unsupported config version. "
                             f"Expected {CFG_VERSION}, "
                             f"found {cfg.CFG_VERSION}")

        self.local_folder = pathlib.Path(missionpath)
        self.remote_folder = (pathlib.Path(cfg.REMOTE_FOLDER)
                              if cfg.REMOTE_FOLDER else None)

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("----")
        self.owner = await self.fetch_user(150625032656125952)

    async def on_message(self, message: Message):
        if self.is_me(message):
            return
        if (message.channel.id not in cfg.CHANNEL_IDS
                and not (message.channel.type == ChannelType.private
                         and message.author == self.owner)):
            # Message was outside of upload channel or owner's DM
            print(f"#{message.channel}: <{message.author}> {message.content}")
            return

        print("Received a message")
        for attachment in message.attachments:
            name = attachment.filename
            if not name.endswith('.pbo'):
                print(f"{name} is not a pbo")
                await message.channel.send("Not a pbo, not uploading")
                return
            print(f"Handling {name}")
            path = self.remote_folder or self.local_folder
            final_path = path / name
            print("Checking existing file")
            try:
                if os.path.isfile(final_path):
                    print(f"{final_path} exists")
                    await message.channel.send(f"File {name} "
                                               "already exists!")
                    return
            except OSError:
                # Will download locally, check the PBO and complain later
                pass
            outfile = self.local_folder / name
            if await attachment.save(outfile) != attachment.size:
                await message.channel.send("Save failed. Request a manual "
                                           "upload or try again.")
                return
            await message.channel.send("Uploaded")
            print("Saved")
            info = get_info(outfile)
            if not info:
                await message.channel.send("Failed to get PBO info")
            else:
                await message.channel.send(info)
            if self.remote_folder:
                print("remote_folder set, moving")
                try:
                    shutil.move(outfile, self.remote_folder / name)
                except (FileNotFoundError, PermissionError, OSError) as e:
                    traceback.print_exc()
                    await message.channel.send(
                            f"{self.owner.mention}: Failed to move "
                            f"the file: {e}")
                else:
                    await message.channel.send("File moved")
                    print("Moved successfully")

    def is_me(self, m):
        return m.author == self.user


if __name__ == "__main__":
    print("Connecting")
    bot = Bot('.')

    bot.run(cfg.TOKEN)
