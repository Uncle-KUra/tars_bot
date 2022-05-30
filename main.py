#!/usr/bin/env python3

from discord.ext import commands

import argparse
import json

from user import UserStorage
from brain import Brain
from text_db import DB


description = '''Stupid queue bot '''
bot = commands.Bot(command_prefix='?', description=description)

db = None
user_storage = None
brain = None


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


async def handle_in(ctx, level):
    display_name = ctx.author.display_name
    uid = ctx.author.id

    print('?in', uid, display_name, level)

    user = user_storage.get_user_from_ctx(ctx)

    for text in brain.in_command(user, level):
        await ctx.send(text)


@bot.command(name='in')
async def in_command(ctx, level: int):
    await handle_in(ctx, level)


@bot.command(name='i')
async def in_command(ctx, level: int):
    await handle_in(ctx, level)


async def handle_out(ctx, *args):
    display_name = ctx.author.display_name
    uid = ctx.author.id
    print('?in', uid, display_name, '|'.join(args))

    user = user_storage.get_user_from_ctx(ctx)

    if len(args) == 1:
        try:
            level = int(args[0])
            for text in brain.out_command_level(user, level):
                await ctx.send(text)
        except ValueError:
            await ctx.send('Cannot parse command from {}'.format(display_name))
    elif len(args) == 0:
        for text in brain.out_command_all(user):
            await ctx.send(text)
    else:
        await ctx.send('Cannot parse command from {}'.format(display_name))


@bot.command(name='out')
async def out(ctx, *args):
    await handle_out(ctx, *args)


@bot.command(name='o')
async def out2(ctx, *args):
    await handle_out(ctx, *args)


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
        bot.run(config['token'])
    else:
        bot.run(config['test_token'])


if __name__ == '__main__':
    main()
