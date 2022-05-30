#!/usr/bin/env python3


class User:
    def __init__(self):
        self.id = None
        self.display_name = None
        self.mention = None

    def update(self, discord_id, display_name, mention):
        self.id = discord_id
        self.display_name = display_name
        self.mention = mention


class UserStorage:
    def __init__(self):
        self.users_data = dict()

    def get_user_from_ctx(self, ctx):
        uid = ctx.author.id
        display_name = ctx.author.display_name
        mention = ctx.author.mention
        if uid not in self.users_data:
            self.users_data[uid] = User()
        user = self.users_data[uid]
        user.update(uid, display_name, mention)
        return user
