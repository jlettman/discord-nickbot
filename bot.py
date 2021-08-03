#!/usr/bin/env python3

import os
import sys
import argparse
import asyncio
import random

import discord
from discord.ext import commands

import argparse

def main():
    global bot, prefix, frequency, channel, message
    sys.stdout.flush()

    parser = argparse.ArgumentParser(
        description=f"Bot for automatically assigning nick names based on roles.")
    parser.add_argument("-p", "--prefix", default="PNP-",
                        help="prefix for roles hinting new nick names")
    parser.add_argument("-f", "--frequency", default=5*60,
                        help="frequency, in seconds, to check members")
    parser.add_argument("-c", "--channel", default="embassy",
                        help="channel to post reminders in")
    parser.add_argument("-m", "--message", action="append", default=[
        "Please do not change your nickname.",
        "Please do not alter your nick."
    ], help="helpful messages to remind the user not to change their nick")

    args = parser.parse_args()
    prefix = args.prefix
    frequency = args.frequency
    channel = args.channel
    message = args.message

    intents = discord.Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix="-nickbot ", intents=intents)

    try:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("error: missing token")
    except Exception as ex:
        print(f"error: parsing environment variables failed: {ex}")
        sys.exit(1)

    bot.loop.create_task(check_names())
    bot.intents
    bot.run(token)


async def check_names():
    global bot, prefix, frequency, channel, message
    await bot.wait_until_ready()

    while True:
        for guild in bot.guilds:
            print(f"◉ Checking guild: {guild}")

            for member in guild.members:
                print(f"  ◎ Checking member: {member}")

                for role in member.roles:
                    if str(role).startswith(prefix):
                        print(f"    ✔ Found prefix: {role}")
                        nick = str(role).replace(prefix, "", 1)

                        if member.nick == nick:
                            print("    ✔ Nick is ok!")
                        else:
                            print("    ✂ Nick is not ok! Fixing that...")
                            try:
                                await member.edit(nick=nick)
                                print("      Fixed!")

                                for c in guild.channels:
                                    if str(c) == channel:
                                        print(
                                            f"    🔊 Located messaging channel {channel}, sending message...")
                                        await c.send(f"{member.mention} {random.choice(message)}")
                                        print("    Done!")
                                        break

                            except Exception as ex:
                                print(f"      Well, that failed: {ex}")

        await asyncio.sleep(frequency)


if __name__ == "__main__":
    main()
