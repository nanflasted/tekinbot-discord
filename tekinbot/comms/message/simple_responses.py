import random

from discord.ext import commands


class SimpleResponses(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def welcome_to_the_jam(self, message):
        choices = [
            'and welcome to the jam',
            'and welcome to japan',
            'if you wanna jam',
        ]
        if message.content.lower().strip() == 'come on and slam':
            await message.channel.send(random.choice(choices))

    @commands.Cog.listener('on_message')
    async def classic_j(self, message):
        choices = [
            'my conscience keeps me petrified',
            'when you left you left me paralyzed',
            'i\'m blue dreaming about the better times',
        ]
        if message.content.lower().startswith(
            'how could i ever sleep at night'
        ):
            await message.channel.send(random.choice(choices))

    @commands.command(
        description="Tekin repeats after you.",
        help="""
        Usage: @TekinBot echo [something]
        Tekinbot says something.
        """
    )
    async def echo(self, ctx, *, message):
        await ctx.send(message)

    @commands.command(
        description="Ping Tekin.",
        help="""
        Usage: @TekinBot ping
        """
    )
    async def ping(self, ctx):
        await ctx.send('Pong')

    @commands.command(
        description="Displays Tekin's github repo",
        help="""
        Usage: @TekinBot gitrepo
        """
    )
    async def gitrepo(self, ctx):
        await ctx.send(
            'https://github.com/nanflasted/tekinbot-discord\n'
            'Talk to @nanflasted to be added to the repo!'
        )


async def setup(bot):
    await bot.add_cog(SimpleResponses(bot))
