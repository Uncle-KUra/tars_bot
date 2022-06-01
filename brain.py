#!/usr/bin/env python3

from collections import defaultdict

from discord_messages import TextMessage

class Brain:
    def __init__(self, user_storage, db):
        self.queue = defaultdict(list)
        for key, value in db.get_collection('queue'):
            if len(key) == 1:
                key = '{key} {simple}'
            self.queue[key] = list(value)
        self.user_storage = user_storage
        self.db = db

    @staticmethod
    def build_key(level, spec):
        return f'{level} {spec if spec else "simple"}'

    def generate_start_text(self, level, spec):
        text = f'Go-go-go! Red Star {level} {spec}\n'
        mentions = []
        key = self.build_key(level, spec)
        for queue_uid in list(self.queue[key]):
            text += f'\t{self.user_storage.get_from_id(queue_uid).display_name}\n'
            mentions.append(self.user_storage.get_from_id(queue_uid).mention)
        text += ' '.join(mentions)
        return text

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

    def get_queue_text(self):
        text = ''
        for key, level, spec in self.generate_all_key_ext():
            if self.queue[key]:
                text += f'Queue for Red Star {level} {spec}\n'
                for uid in self.queue[key]:
                    text += '\t{}\n'.format(self.user_storage.get_from_id(uid).display_name)
        if not text:
            text = 'Empty queue'
        return text

    def q_command(self):
        yield TextMessage(self.get_queue_text())

    def in_command(self, user, level, spec):
        key = self.build_key(level, spec)
        if user.id not in self.queue[key]:
            self.queue[key].append(user.id)
            yield TextMessage(f'{user.display_name} enters queue for Red Star {level} {spec}')
            lq = len(self.queue[key])
            if lq == 4 or lq == 2 and (level == 2 or spec == 'duo' or spec == 'dark'):
                yield TextMessage(self.generate_start_text(level, spec))
                for queue_uid in list(self.queue[key]):
                    self.clear_user_from_queue(queue_uid)
            self.db.set_collection('queue', self.queue)
            self.db.save()
            yield TextMessage(self.get_queue_text())
        else:
            yield TextMessage(f'{user.display_name} already in queue for Red Star {level} {spec}')

    def out_command_level(self, user, level, spec):
        key = self.build_key(level, spec)
        if user.id not in self.queue[key]:
            yield TextMessage(f'{user.display_name} not in queue for Red Star {level} {spec}')
        else:
            self.queue[key].remove(user.id)
            self.db.set_collection('queue', self.queue)
            self.db.save()
            yield TextMessage(f'{user.display_name} leaves queue for Red Star {level} {spec}')
            yield TextMessage(self.get_queue_text())

    def out_command_all(self, user):
        if self.clear_user_from_queue(user.id):
            self.db.set_collection('queue', self.queue)
            self.db.save()
        yield TextMessage(f'{user.display_name} leaves queue for every Red Star')
        yield TextMessage(self.get_queue_text())
