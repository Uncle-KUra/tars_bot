#!/usr/bin/env python3

from collections import defaultdict


class Brain:
    def __init__(self, user_storage, db):
        self.queue = defaultdict(list)
        for key, value in db.get_collection('queue'):
            self.queue[int(key)] = list(value)
        self.user_storage = user_storage
        self.db = db

    def generate_start_text(self, level):
        text = 'Go-go-go! Rs{}\n'.format(level)
        mentions = []
        for queue_uid in list(self.queue[level]):
            text += '\t{}\n'.format(self.user_storage.get_from_id(queue_uid).display_name)
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

    def get_queue_text(self):
        text = ''
        for level in self.queue:
            if self.queue[level]:
                text += 'Queue for rs{}\n'.format(level)
                for uid in self.queue[level]:
                    text += '\t{}\n'.format(self.user_storage.get_from_id(uid).display_name)
        if not text:
            text = 'Empty queue'
        return text

    def q_command(self):
        yield self.get_queue_text()

    def in_command(self, user, level):
        if user.id not in self.queue[level]:
            self.queue[level].append(user.id)
            yield '{} enters queue for rs{}'.format(user.display_name, level)
            if len(self.queue[level]) == 4 or level == 2 and len(self.queue[level]) == 2:
                yield self.generate_start_text(level)
                for queue_uid in list(self.queue[level]):
                    self.clear_user_from_queue(queue_uid)
            self.db.set_collection('queue', self.queue)
            self.db.save()
            yield self.get_queue_text()
        else:
            yield '{} already in queue for rs{}'.format(user.display_name, level)

    def out_command_level(self, user, level):
        if user.id not in self.queue[level]:
            yield '{} not in queue for rs{}'.format(user.display_name, level)
        else:
            self.queue[level].remove(user.id)
            self.db.set_collection('queue', self.queue)
            self.db.save()
            yield '{} leaves queue for rs{}'.format(user.display_name, level)
            yield self.get_queue_text()

    def out_command_all(self, user):
        if self.clear_user_from_queue(user.id):
            self.db.set_collection('queue', self.queue)
            self.db.save()
        yield '{} leaves queue for every rs'.format(user.display_name)
        yield self.get_queue_text()
