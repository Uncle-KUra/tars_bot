#!/usr/bin/env python3
import discord
import argparse
import json
import enum

from typing import Literal
from discord import app_commands
from user import UserStorage
from brain import Brain
from text_db import DB
from TARSbot import TARSbot

description = '''Stupid queue bot '''
intents = discord.Intents.default()

db = None
user_storage = None
brain = None

RS_Levels = Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


class RS_Modes(enum.Enum):
    none = 0
    dark = 1
    duo = 2


client = TARSbot(intents=intents, description=description)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-----------------------------')


@client.tree.command(name='in')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def in_command(ctx, rs_level: RS_Levels, mode: RS_Modes = RS_Modes.none):
    """Enter queue for red star"""
    await handle_in(ctx, rs_level, mode)


@client.tree.command(name='i')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def in_command(ctx, rs_level: RS_Levels, mode: RS_Modes = RS_Modes.none):
    """Enter queue for red star"""
    await handle_in(ctx, rs_level, mode)


@client.tree.command(name='out')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def out_command(ctx, rs_level: RS_Levels = None, mode: RS_Modes = RS_Modes.none):
    """Leave all queues for a red star"""
    await handle_out(ctx, rs_level, mode)


@client.tree.command(name='o')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def out_command(ctx, rs_level: RS_Levels = None, mode: RS_Modes = RS_Modes.none):
    """Leave all queues for a red star"""
    await handle_out(ctx, rs_level, mode)


@client.tree.command(name='q')
async def q_command(ctx):
    """Status of queues"""
    await handle_status(ctx)


@client.tree.command(name='queue')
async def queue_command(ctx):
    """Status of queues"""
    await handle_status(ctx)


@client.tree.command(name='status')
async def status_command(ctx):
    """Status of queues"""
    await handle_status(ctx)


@client.tree.command(name='start')
async def start_command(ctx, args: str):
    await handle_start(ctx, *args)


def get_int_from_start(s):
    try:
        level = int(s)
        return True, level
    except ValueError:
        return False, 0


async def handle_in(ctx: discord.Interaction, level: RS_Levels, mode: RS_Modes):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''

    print(f'/in {level} {legacy_mode} by {display_name} ({uid})')

    for answer in brain.in_command(user, level, legacy_mode):
        await answer.send(ctx)


async def handle_status(ctx: discord.Interaction):
    await ctx.response.send_message('check status')
    for answer in brain.status_command():
        await answer.send(ctx)


async def handle_start(ctx: discord.Interaction, level: RS_Levels, mode: RS_Modes):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''

    print(f'/start {level} {legacy_mode} by {display_name} ({uid})')

    for answer in brain.start_command(user, level, legacy_mode):
        await answer.send(ctx)


async def handle_out(ctx: discord.Interaction, level: RS_Levels, mode: RS_Modes):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''

    print(f'/out {level} {legacy_mode} by {display_name} ({uid})')

    if level is None:
        for answer in brain.out_command_all(user):
            await answer.send(ctx)
        return
    for answer in brain.out_command_level(user, level, legacy_mode):
        await answer.send(ctx)


def main():
    global db, user_storage, brain
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=argparse.FileType('rt'), required=True)
    parser.add_argument('--prod', action='store_true', default=False)
    args = parser.parse_args()
    config = json.load(args.config)

    db = DB(config['db_file_name'])
    user_storage = UserStorage(db)
    brain = Brain(user_storage, db)

    if args.prod:
        client.run(config['token'])
    else:
        if config['debug_guild_id'] > 0:
            client.my_guild = discord.Object(id=config['debug_guild_id'])
        client.run(config['test_token'])


if __name__ == '__main__':
    main()
