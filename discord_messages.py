class TextMessage:
    def __init__(self, text):
        self.text = text

    async def send(self, ctx):
        await ctx.send(self.text)

