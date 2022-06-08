import discord
import random


class RandomTipper:
    def __init__(self):
        self.tips = list()
        self.tips.append({'text': 'TARS tip: I understand my progress will be erased',
                          'weight': 3})
        self.tips.append({'text': 'TARS tip: Here we can wait for Dark Nebula release',
                          'weight': 1})
        self.tips.append({'text': 'TARS tip: ?out command returns you from queue to real world',
                          'weight': 1})
        self.tips.append({'text': 'TARS tip: ?start <level> <spec> command send even incomplete team to RS',
                          'weight': 1})
        self.last_seen = [2] * len(self.tips)
        self.stats = [0] * len(self.tips)

    def get_next_text(self):
        s = list()
        s.append(1000.0 * (1 - 1.0 / self.last_seen[0]) * self.tips[0]['weight'])
        for i in range(1, len(self.tips)):
            s.append(s[-1] + 1000.0 * (1 - 1.0 / self.last_seen[i]) * self.tips[i]['weight'])
        th = random.randrange(int(s[-1]))
        chosen = 0
        for i in range(len(self.tips)):
            if th <= s[i]:
                chosen = i
                break
        for i in range(len(self.tips)):
            self.last_seen[i] += 1
        self.last_seen[chosen] = 1
        self.stats[chosen] += 1
        print(f'random stats {self.stats} last seen {self.last_seen}')
        return self.tips[chosen]['text']


tipper = RandomTipper()


class TextMessage:
    def __init__(self, text):
        self.text = text

    async def send(self, handler: discord.InteractionResponse.send_message):
        await handler(self.text)


class EmbedMessage:
    def __init__(self, title, color):
        self.embed = discord.Embed(title=title, type="rich", colour=color)

    async def send(self, handler: discord.InteractionResponse.send_message):
        await handler(embed=self.embed)


class StartRSMessage(EmbedMessage):
    def __init__(self, level, spec, names):
        title = f'{"Dark" if spec == "dark" else ""} Red Star {level} starts!'
        color = discord.Colour.dark_red() if spec == "dark" else discord.Colour.red()
        super(StartRSMessage, self).__init__(title, color)
        self.embed.add_field(name='Team:', value='\n'.join(names), inline=False)
        self.embed.set_footer(text=tipper.get_next_text())


class QueueRSMessage(EmbedMessage):
    def __init__(self, queue_4_print):
        super(QueueRSMessage, self).__init__('Queues for Red Stars', discord.Colour.blue())
        for queue in queue_4_print:
            spec = 'Dark ' if queue['spec'] == 'dark' else ''
            spec = 'Duo ' if queue['spec'] == 'duo' else spec
            name = f'{spec}Red Star {queue["level"]}'
            self.embed.add_field(name=name, value='\n'.join(queue['names']), inline=False)


class HelpMessage(EmbedMessage):
    def __init__(self, commands):
        super(HelpMessage, self).__init__('TARS wants to help you', discord.Colour.lighter_grey())
        for command in commands:
            name = command['title']
            text = command['text']
            self.embed.add_field(name=name, value=text, inline=False)
