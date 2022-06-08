#!/usr/bin/env python3

from collections import defaultdict
import asyncio

from discord_messages import TextMessage
from discord_messages import StartRSMessage
from discord_messages import QueueRSMessage


class Brain:
    def __init__(self, user_storage, db):
        self.queue = defaultdict(list)
        for key, value in db.get_collection('queue'):
            if len(key) == 1:
                key = '{key} {simple}'
            self.queue[key] = list(value)
        self.user_storage = user_storage
        self.db = db
        self.lock = asyncio.Lock()

    @staticmethod
    def build_key(level, spec):
        return f'{level} {spec if spec else "simple"}'

    def generate_start_text(self, level, spec):
        key = self.build_key(level, spec)
        mentions = []
        names = []
        for queue_uid in list(self.queue[key]):
            user = self.user_storage.get_from_id(queue_uid)
            if user:
                names.append(user.display_name)
                mentions.append(user.mention)
            else:
                print(f'user not found at generate start text {queue_uid}')
                names.append(str(queue_uid))
        yield StartRSMessage(level, spec, names)
        yield TextMessage(' '.join(mentions))

    def clear_user_from_queue(self, uid):
        ok = False
        for que in self.queue.values():
            try:
                que.remove(uid)
                ok = True
            except ValueError:
                pass
        return ok

    @staticmethod
    def generate_all_keys():
        for i in range(2, 5):
            yield i, 'simple'
            yield i, 'duo'
        for i in range(5, 13):
            yield i, 'simple'
            yield i, 'duo'
            yield i, 'dark'

    def generate_all_key_ext(self):
        for level, spec in self.generate_all_keys():
            yield self.build_key(level, spec), level, (spec if spec != 'simple' else '')

    def generate_queue_text(self):
        queue_4_print = []
        for key, level, spec in self.generate_all_key_ext():
            if self.queue[key]:
                names = []
                for uid in self.queue[key]:
                    user = self.user_storage.get_from_id(uid)
                    if user:
                        names.append(user.display_name)
                    else:
                        names.append(str(uid))
                        print(f'user not found at generate queue text {uid}')
                queue_4_print.append({'level': level, 'spec': spec,
                                      'names': names})
        if queue_4_print:
            yield QueueRSMessage(queue_4_print)
        else:
            yield TextMessage('Empty queue')

    def status_command(self):
        with self.lock:
            yield from self.generate_queue_text()

    def in_command(self, user, level, spec):
        with self.lock:
            key = self.build_key(level, spec)
            if user.id not in self.queue[key]:
                self.queue[key].append(user.id)
                yield TextMessage(f'{user.display_name} enters queue for Red Star {level} {spec}')
                lq = len(self.queue[key])
                if lq == 4 or lq == 2 and (level == 2 or spec == 'duo' or spec == 'dark'):
                    yield from self.generate_start_text(level, spec)
                    for queue_uid in list(self.queue[key]):
                        self.clear_user_from_queue(queue_uid)
                self.db.set_collection('queue', self.queue)
                self.db.save()
                yield from self.generate_queue_text()
            else:
                yield TextMessage(f'{user.display_name} already in queue for Red Star {level} {spec}')

    def out_level_command(self, user, level, spec):
        with self.lock:
            key = self.build_key(level, spec)
            if user.id not in self.queue[key]:
                yield TextMessage(f'{user.display_name} not in queue for Red Star {level} {spec}')
            else:
                self.queue[key].remove(user.id)
                self.db.set_collection('queue', self.queue)
                self.db.save()
                yield TextMessage(f'{user.display_name} leaves queue for Red Star {level} {spec}')
                yield from self.generate_queue_text()

    def start_command(self, user, level, spec):
        with self.lock:
            key = self.build_key(level, spec)
            if user.id not in self.queue[key]:
                yield TextMessage(f'{user.display_name} not in queue for Red Star {level} {spec}')
            else:
                yield TextMessage(f'{user.display_name} starts queue for Red Star {level} {spec}')
                yield from self.generate_start_text(level, spec)
                for queue_uid in list(self.queue[key]):
                    self.clear_user_from_queue(queue_uid)
                self.db.set_collection('queue', self.queue)
                self.db.save()
                yield from self.generate_queue_text()

    def out_all_command(self, user):
        with self.lock:
            if self.clear_user_from_queue(user.id):
                self.db.set_collection('queue', self.queue)
                self.db.save()
            yield TextMessage(f'{user.display_name} leaves queue for every Red Star')
            yield from self.generate_queue_text()
