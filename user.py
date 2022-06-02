#!/usr/bin/env python3

import discord

class User:
    def __init__(self):
        self.id = None
        self.display_name = None
        self.mention = None

    def update(self, discord_id, display_name, mention):
        if self.id == discord_id and self.display_name == display_name and self.mention == self.mention:
            return False
        self.id = discord_id
        self.display_name = display_name
        self.mention = mention
        return True

    def update_from_dict(self, data):
        self.id = data['id']
        self.display_name = data['display_name']
        self.mention = data['mention']

    def save_to_json(self):
        return {'id': self.id, 'display_name': self.display_name, 'mention': self.mention}


class UserStorage:
    def __init__(self, db):
        self.users_data = dict()
        for uid, single_user in db.get_collection('users'):
            self.users_data[int(uid)] = User()
            self.users_data[int(uid)].update_from_dict(single_user)
        self.db = db

    def get_user_from_ctx(self, ctx: discord.Interaction):
        uid = ctx.user.id
        display_name = ctx.user.display_name
        mention = ctx.user.mention
        if uid not in self.users_data:
            self.users_data[uid] = User()
        user = self.users_data[uid]
        if user.update(uid, display_name, mention):
            self.db.set_collection_value('users', uid, user.save_to_json())
            self.db.save()
        return user

    def get_from_id(self, uid):
        return self.users_data[uid]
