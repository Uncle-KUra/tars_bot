#!/usr/bin/env python3
import discord
import argparse
import json

from user import UserStorage
from brain import Brain
from text_db import DB
from TARSbot import TARSbot

description = '''Stupid queue bot '''
intents = discord.Intents.default()

db = None
user_storage = None
brain = None

client = TARSbot(intents=intents, description=description)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-----------------------------')


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command(name='in')
async def in_command(ctx, args: str):
    await handle_in(ctx, *args)


@client.tree.command(name='i')
async def in_command(ctx, args: str):
    await handle_in(ctx, *args)


@client.tree.command(name='out')
async def out(ctx):
    await handle_out(ctx)


@client.tree.command(name='o')
async def out2(ctx):
    await handle_out(ctx)


@client.tree.command(name='q')
async def q_command(ctx):
    await handle_status(ctx)


@client.tree.command(name='queue')
async def queue_command(ctx):
    await handle_status(ctx)


@client.tree.command(name='status')
async def status_command(ctx):
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


async def handle_in(ctx: discord.Interaction, *args):
    display_name = ctx.user.display_name
    uid = ctx.user.id

    print('?in', uid, display_name, '|'.join(args))

    error_message = '{}, please enter star level: "?in 3" "?in 2 duo" "?in 5 dark"'.format(display_name)

    if len(args) == 0:
        await ctx.response.send_message(error_message)
        return
    elif len(args) == 1:
        ok, level = get_int_from_start(args[0])
        if not ok:
            await ctx.response.send_message(error_message)
            return
        spec = ''
    elif len(args) == 2:
        ok, level = get_int_from_start(args[0])
        spec = args[1].lower()
        if not ok or spec not in ('duo', 'dark'):
            ok, level = get_int_from_start(args[1])
            spec = args[0].lower()
            if not ok or spec not in ('duo', 'dark'):
                await ctx.response.send_message(error_message)
                return
    else:
        await ctx.response.send_message(error_message)
        return

    user = user_storage.get_user_from_ctx(ctx)

    for answer in brain.in_command(user, level, spec):
        await answer.send(ctx)


async def handle_status(ctx: discord.Interaction):
    await ctx.response.send_message('check status')
    for answer in brain.status_command():
        await answer.send(ctx)


async def handle_start(ctx: discord.Interaction, *args):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    print('?start', uid, display_name, '|'.join(args))

    user = user_storage.get_user_from_ctx(ctx)

    if len(args) == 0:
        await ctx.response.send_message(f'Start command need star level - ?start <level> <mode>')
        return
    elif len(args) > 2:
        await ctx.response.send_message(f'Cannot parse command from {display_name}')
        return
    elif len(args) == 1:
        try:
            level = int(args[0])
            spec = ''
        except ValueError:
            await ctx.response.send_message(f'Cannot parse command from {display_name}')
            return
    elif len(args) == 2:
        ok, level = get_int_from_start(args[0])
        spec = args[1].lower()
        if not ok or spec not in ('duo', 'dark'):
            ok, level = get_int_from_start(args[1])
            spec = args[0].lower()
            if not ok or spec not in ('duo', 'dark'):
                await ctx.response.send_message(f'Cannot parse command from {display_name}')
                return
    for answer in brain.start_command(user, level, spec):
        await answer.send(ctx)


async def handle_out(ctx: discord.Interaction, *args):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    print('?out', uid, display_name, '|'.join(args))

    user = user_storage.get_user_from_ctx(ctx)

    if len(args) == 0:
        for answer in brain.out_command_all(user):
            await answer.send(ctx)
        return
    elif len(args) > 2:
        await ctx.response.send_message(f'Cannot parse command from {display_name}')
        return
    elif len(args) == 1:
        try:
            level = int(args[0])
            spec = ''
            for answer in brain.out_command_level(user, level, spec):
                await answer.send(ctx)
        except ValueError:
            await ctx.response.send_message(f'Cannot parse command from {display_name}')
            return
    elif len(args) == 2:
        ok, level = get_int_from_start(args[0])
        spec = args[1].lower()
        if not ok or spec not in ('duo', 'dark'):
            ok, level = get_int_from_start(args[1])
            spec = args[0].lower()
            if not ok or spec not in ('duo', 'dark'):
                await ctx.response.send_message(f'Cannot parse command from {display_name}')
                return
    for answer in brain.out_command_level(user, level, spec):
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
