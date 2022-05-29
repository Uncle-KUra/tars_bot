#!/usr/bin/env python3

import discord
from discord.ext import commands

from collections import defaultdict
import argparse
import json


description = '''Stupid queue bot '''
bot = commands.Bot(command_prefix='?', description=description)

queue = defaultdict(list)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


def get_queue_list():
    text = ''
    for level in queue:
        if queue[level]:
            text += 'Queue for rs{}\n'.format(level)
            for user_name in queue[level]:
                text += '\t{}\n'.format(user_name)
    if not text:
        text = 'Empty queue'
    return text


@bot.command(name='in')
async def in_command(ctx, level: int):
    print('in!')
    user_name = ctx.author.name
    if user_name not in queue[level]:
        queue[level].append(user_name)
        await ctx.send('{} enters queue for rs{}'.format(user_name, level))
        if len(queue[level]) == 4 or level == 2 and len(queue[level]) == 2:
            text = 'Go-go-go! Rs{}\n'.format(level)
            for queue_user_name in queue[level]:
                text += '\t{}\n'.format(queue_user_name)
            queue[level].clear()
            await ctx.send(text)
        await ctx.send(get_queue_list())
    else:
        await ctx.send('{} already in queue for rs{}'.format(user_name, level))


@bot.command()
async def out(ctx, level: int):
    user_name = ctx.author.name
    if user_name not in queue[level]:
        await ctx.send('{} not in queue for rs{}'.format(user_name, level))
    else:
        queue[level].remove(user_name)
        await ctx.send('{} leaves queue for rs{}'.format(user_name, level))
        await ctx.send(get_queue_list())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=argparse.FileType('rt'), required=True)
    parser.add_argument('--prod', action='store_true', default=False)
    args = parser.parse_args()
    config = json.load(args.config)
    if args.prod:
        bot.run(config['token'])
    else:
        bot.run(config['test_token'])
