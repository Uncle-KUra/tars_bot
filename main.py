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

from parsers import stupid_tokenize
from parsers import parse_all

from discord_messages import HelpMessage
from discord_messages import TextMessage

description = '''Stupid queue bot '''
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


db = None
user_storage = None
brain = None

RS_Levels = Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


class RedStarModes(enum.Enum):
    none = 0
    dark = 1
    duo = 2


client = TARSbot(intents=intents, description=description)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-----------------------------')


def process_help(_, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    commands = [{'title': 'Help', 'text': '?help / ?h - print this help'}]
    command.append({'title': 'Enter a queue', 'text': '?in <level> <mode> - enter queue for specific RS level and mode. Example: ?in 4 / ?in 5 dark'})
    command.append({'title': 'Enter a queue for dark mode', 'text': '?dark <level> - enter queue for specific DRS level. Example: ?dark 4'})
    command.append({'title': 'Leave a queue', 'text': '?out <level> <mode> - leave queue for specific level and mode. Example: ?out 3 / ?in 7 duo'})
    command.append({'title': 'Leave all queues', 'text': '?out - leave all queue'})
    command.append({'title': 'Start uncomplete', 'text': '?start <level> <mode> - start red start for specific level and mode'})
    command.append({'title': 'Show queues status', 'text': '?status - leave all queue'})
    yield HelpMessage(commands)


def process_full_out(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_out_impl(message.author, None, '')


def process_level_out(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_out_impl(message.author, command.params['level'], command.params.get('mode', ''))


def process_level_in(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_in_impl(message.author, command.params['level'], command.params.get('mode', ''))


def process_level_start(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_start_impl(message.author, command.params['level'], command.params.get('mode', ''))


def process_level_dark(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_in_impl(message.author, command.params['level'], 'dark')


def process_level_duo(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_in_impl(message.author, command.params['level'], 'duo')


def process_status(_, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_status_impl()


processors = {
    'help': process_help,
    'full_out': process_full_out,
    'level_out': process_level_out,
    'level_in': process_level_in,
    'level_start': process_level_start,
    'level_dark': process_level_dark,
    'level_duo': process_level_duo,
    'status': process_status
}


@client.event
async def on_message(message):
    if message.author.bot:
        return
    parts = stupid_tokenize(message.content)
    command = parse_all(parts)
    if command:
        processor = processors.get(command.command, None)
    if not processor:
        return
    for answer in processor(message, command):
        await answer.send(message.channel)


@client.tree.command(name='in')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def in_command(ctx, rs_level: RS_Levels, mode: RedStarModes = RedStarModes.none):
    """enter queue for red star"""
    await handle_in(ctx, rs_level, mode)


@client.tree.command(name='i')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def in_command(ctx, rs_level: RS_Levels, mode: RedStarModes = RedStarModes.none):
    """enter queue for red star"""
    await handle_in(ctx, rs_level, mode)


@client.tree.command(name='out')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def out_command(ctx, rs_level: RS_Levels = None, mode: RedStarModes = RedStarModes.none):
    """leave all queues for a red star"""
    await handle_out(ctx, rs_level, mode)


@client.tree.command(name='o')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def out_command(ctx, rs_level: RS_Levels = None, mode: RedStarModes = RedStarModes.none):
    """leave all queues for a red star"""
    await handle_out(ctx, rs_level, mode)


@client.tree.command(name='q')
async def q_command(ctx):
    """status of queues"""
    await handle_status(ctx)


@client.tree.command(name='queue')
async def queue_command(ctx):
    """status of queues"""
    await handle_status(ctx.channel)


@client.tree.command(name='status')
async def status_command(ctx):
    """status of queues"""
    await handle_status(ctx.channel)


@client.tree.command(name='start')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def start_command(ctx, rs_level: RS_Levels, mode: RedStarModes = RedStarModes.none):
    """starts queue for red star"""
    await handle_start(ctx, rs_level, mode)


def handle_in_impl(user, level, legacy_mode):
    yield from brain.in_command(user, level, legacy_mode)


async def handle_in(ctx: discord.Interaction, level: RS_Levels, mode: RedStarModes):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''

    print(f'/in {level} {legacy_mode} by {display_name} ({uid})')

    for answer in handle_in_impl(user, level, legacy_mode):
        await answer.send(ctx.channel)


def handle_status_impl():
    yield from brain.status_command()


async def handle_status(ctx: discord.Interaction):
    await ctx.response.send_message('check status')
    for answer in handle_status_impl:
        await answer.send(ctx.channel)


def handle_start_impl(user, level, legacy_mode):
    yield from brain.start_command(user, level, legacy_mode)


async def handle_start(ctx: discord.Interaction, level: RS_Levels, mode: RedStarModes):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''

    print(f'/start {level} {legacy_mode} by {display_name} ({uid})')

    for answer in handle_start_impl(user, level, legacy_mode):
        await answer.send(ctx.channel)


def handle_out_impl(user: discord.user, level: RS_Levels, mode: str):
    if level is None:
        yield from brain.out_command_all(user)
        return
    yield from brain.out_command_level(user, level, mode)


async def handle_out(ctx: discord.Interaction, level: RS_Levels, mode: RedStarModes):
    display_name = ctx.user.display_name
    uid = ctx.user.id
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''

    print(f'/out {level} {legacy_mode} by {display_name} ({uid})')

    for answer in handle_out_impl(user, level, legacy_mode):
        await answer.send(ctx.channel)


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
