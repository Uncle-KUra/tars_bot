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
    commands = [{'title': 'Help', 'text': '?help / ?h - print this help'}, {'title': 'Enter a queue',
                                                                            'text': '?in <level> <mode> - enter queue for specific RS level and mode. \nExample: ?in 4 / ?in 5 dark'},
                {'title': 'Enter a queue for dark mode',
                 'text': '?dark <level> - enter queue for specific DRS level. \nExample: ?dark 4'},
                {'title': 'Leave a queue',
                 'text': '?out <level> <mode> - leave queue for specific level and mode. \nExample: ?out 3 / ?in 7 duo'},
                {'title': 'Leave all queues', 'text': '?out - leave all queue'}, {'title': 'Start uncomplete',
                                                                                  'text': '?start <level> <mode> - start red start for specific level and mode'},
                {'title': 'Show queues status', 'text': '?status - leave all queue'}]
    yield HelpMessage(commands)


def process_full_out(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_out(message.author, None, '')


def process_level_out(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_out(message.author, command.params['level'], command.params.get('mode', ''))


def process_level_in(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_in(message.author, command.params['level'], command.params.get('mode', ''))


def process_level_start(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_start(message.author, command.params['level'], command.params.get('mode', ''))


def process_level_dark(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_in(message.author, command.params['level'], 'dark')


def process_level_duo(message, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_in(message.author, command.params['level'], 'duo')


def process_status(_, command):
    if command.hard:
        yield TextMessage('Was hard but I got it')
    yield from handle_status()


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
    processor = processors.get(command.command, None) if command else None
    if not processor:
        return
    for answer in processor(message, command):
        await answer.send(message.channel.send)


@client.tree.command(name='in')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def in_command(ctx: discord.Interaction, rs_level: RS_Levels, mode: RedStarModes = RedStarModes.none):
    """enter queue for red star"""
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''
    answers = handle_in(user, rs_level, legacy_mode)

    await next(answers).send(ctx.response.send_message)

    for answer in answers:
        await answer.send(ctx.channel.send)


@client.tree.command(name='out')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def out_command(ctx: discord.Interaction, rs_level: RS_Levels = None, mode: RedStarModes = RedStarModes.none):
    """leave all queues for a red star"""
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''
    answers = handle_out(user, rs_level, legacy_mode)

    await next(answers).send(ctx.response.send_message)

    for answer in answers:
        await answer.send(ctx.channel.send)


@client.tree.command(name='queue')
async def queue_command(ctx: discord.Interaction):
    """status of queues"""

    answers = handle_status()
    await next(answers).send(ctx.response.send_message)

    for answer in answers:
        await answer.send(ctx.channel.send)


@client.tree.command(name='status')
async def status_command(ctx: discord.Interaction):
    """status of queues"""

    answers = handle_status()
    await next(answers).send(ctx.response.send_message)

    for answer in answers:
        await answer.send(ctx.channel.send)


@client.tree.command(name='start')
@app_commands.describe(
    rs_level='Red star level',
    mode='Queue mode',
)
async def start_command(ctx, rs_level: RS_Levels, mode: RedStarModes = RedStarModes.none):
    """starts queue for red star"""
    user = user_storage.get_user_from_ctx(ctx)
    legacy_mode = mode.name if (mode.value > 0) else ''
    answers = handle_start(user, rs_level, legacy_mode)

    next(answers).send(ctx.response.send_message)

    for answer in answers:
        await answer.send(ctx.channel.send)


def handle_in(user, level, legacy_mode):
    print(f'im {level} {legacy_mode} by {user.display_name} ({user.id})')

    yield from brain.in_command(user, level, legacy_mode)


def handle_status():
    yield from brain.status_command()


def handle_start(user, level, legacy_mode):
    print(f'start {level} {legacy_mode} by {user.display_name} ({user.id})')

    yield from brain.start_command(user, level, legacy_mode)


def handle_out(user: discord.user, level: RS_Levels, mode: str):
    print(f'out {level} {mode} by {user.display_name} ({user.id})')

    if level is None:
        yield from brain.out_command_all(user)
        return
    yield from brain.out_command_level(user, level, mode)


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
