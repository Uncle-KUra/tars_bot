import discord


class TextMessage:
    def __init__(self, text):
        self.text = text

    async def send(self, ctx):
        await ctx.send(self.text)


class StartRSMessage:
    def __init__(self, level, spec, names):
        title = f'{"Dark" if spec == "dark" else ""} Red Star {level} starts!'
        color = discord.Colour.dark_red() if spec == "dark" else discord.Colour.red()
        self.embed = discord.Embed(title=title, type="rich", colour=color)
        self.embed.add_field(name='Team:', value='\n'.join(names), inline=False)

    async def send(self, ctx):
        await ctx.send(embed=self.embed)


class QueueRSMessage:
    def __init__(self, queue_4_print):
        color = discord.Colour.blue()
        title = f'Queues for Red Stars'
        self.embed = discord.Embed(title=title, type="rich", colour=color)
        for queue in queue_4_print:
            spec = 'Dark ' if queue['spec'] == 'dark' else ''
            spec = 'Duo ' if queue['spec'] == 'duo' else spec
            name = f'{spec}Red Star {queue["level"]}'
            self.embed.add_field(name=name, value='\n'.join(queue['names']), inline=False)

    async def send(self, ctx):
        await ctx.send(embed=self.embed)

