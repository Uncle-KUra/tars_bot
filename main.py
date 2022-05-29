#!/usr/bin/env python3

import discord
from discord.ext import commands

from collections import defaultdict
import argparse
import json

DISPLAY_NAME = 'display_name'
MENTION = 'mention'


description = '''Stupid queue bot '''
bot = commands.Bot(command_prefix='?', description=description)

queue = defaultdict(list)
users_data = dict()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


def get_queue_list_text():
    text = ''
    for level in queue:
        if queue[level]:
            text += 'Queue for rs{}\n'.format(level)
            for uid in queue[level]:
                text += '\t{}\n'.format(users_data[uid][DISPLAY_NAME])
    if not text:
        text = 'Empty queue'
    return text


def update_user_data(ctx):
    uid = ctx.author.id
    display_name = ctx.author.display_name
    mention = ctx.author.mention
    users_data[uid] = {DISPLAY_NAME: display_name,
                       MENTION: mention}


def clear_user_from_queue(uid):
    for que in queue.values():
        que.remove(uid)


def generate_start_text(level):
    text = 'Go-go-go! Rs{}\n'.format(level)
    mentions = []
    for queue_uid in list(queue[level]):
        text += '\t{}\n'.format(users_data[queue_uid][DISPLAY_NAME])
        mentions.append(users_data[queue_uid][MENTION])
    text += ' '.join(mentions)
    return text


@bot.command(name='in')
async def in_command(ctx, level: int):
    display_name = ctx.author.display_name
    uid = ctx.author.id

    print('?in', uid, display_name, level)

    update_user_data(ctx)

    if uid not in queue[level]:
        queue[level].append(uid)
        await ctx.send('{} enters queue for rs{}'.format(display_name, level))
        if len(queue[level]) == 4 or level == 2 and len(queue[level]) == 2:
            text = generate_start_text(level)
            for queue_uid in list(queue[level]):
                clear_user_from_queue(queue_uid)
            await ctx.send(text)
        await ctx.send(get_queue_list_text())
    else:
        await ctx.send('{} already in queue for rs{}'.format(display_name, level))


@bot.command()
async def out(ctx, level: int):
    display_name = ctx.author.display_name
    uid = ctx.author.id

    print('?in', uid, display_name, level)
    if uid not in queue[level]:
        await ctx.send('{} not in queue for rs{}'.format(display_name, level))
    else:
        queue[level].remove(uid)
        await ctx.send('{} leaves queue for rs{}'.format(display_name, level))
        await ctx.send(get_queue_list_text())


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
