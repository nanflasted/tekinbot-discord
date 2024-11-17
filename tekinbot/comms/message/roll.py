import random
import re
import time

from discord.ext import commands


class RandomRolls(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.magic_msgs = [
            # positive
            'It is certain.', 'It is decidedly so.', 'Without a doubt.',
            'Yes - definitely.', 'You may rely on it.', 'As I see it, yes.',
            'Most likely.', 'Outlook Good.', 'Yes.', 'Signs point to yes.',
            # neutral
            'Reply hazy, try again.', 'Ask again later.',
            'Better not tell you now.', 'Cannot predict now.',
            'Concentrate and ask again.',
            # negative
            'Don\'t count on it.', 'My reply is no.', 'My sources say no.',
            'Outlook not so good.', 'Very doubtful.'
        ]
        random.seed(time.time())

    @commands.command(
        description="Ask Tekin to roll some dies.",
        help="""
        Usage: @TekinBot roll ndm [purpose] or @TekinBot roll n dm [purpose]
        where n is the number of dies, and m is the type of dies.
        If n is not specified it is considered 1, and with a maximum of 100.
        Purposes are ignored by Tekin.
        """
    )
    async def roll(self, ctx, *, arg):
        roll_rgx = r'(?P<num_d>[\d]+)? ?d(?P<d_type>[\d]+).*'
        match = re.fullmatch(roll_rgx, arg)
        num_d = 1 if not match.group('num_d') else int(match.group('num_d'))
        d_type = int(match.group('d_type'))

        if num_d > 100:
            return await ctx.send(
                'Ehh I don\'t have this many dice to roll; '
                'I\'ve only got :100:'
            )

        rolls = [random.randint(1, d_type) for _ in range(num_d)]

        await ctx.send(
            f'Ok, {ctx.author.mention}, here are the rolls: {rolls}'
        )

    @commands.command(
        description="Ask Tekin to make a choice",
        help="""
        Usage: @TekinBot choose choice1 [choice2 choice3 ...]
        Thanks @meekers for this function.
        """
    )
    async def choose(self, ctx, *choices):
        choices = list(map(lambda x: x.split(',')[0], choices))
        num_ch = len(choices)
        # Choose an option randomly
        chosen = random.choice(choices).strip()
        # Remove or if needed
        if chosen[:3] == "or ":
            chosen = chosen[3:].strip()
        # Come up with a valid chance
        chance = 100/num_ch + max([
            random.randint(0, int(100-(100/num_ch))) for _ in range(num_ch)
        ])
        await ctx.send(
            f'I am {chance}% sure '
            f'{ctx.author.mention} should choose {chosen}.'
        )

    @commands.command(
        aliases=['8ball'],
        description="Ask Tekin to look into the magic 8ball",
        help="""
        Usage: @TekinBot magic8 [question] or @TekinBot 8ball [question]
        """
    )
    async def magic8(self, ctx, *, question):
        await ctx.send(
            f'{ctx.author.mention} asked:\n'
            f'> {question}\n'
            f'{random.choice(self.magic_msgs)}'
        )


async def setup(bot):
    await bot.add_cog(RandomRolls(bot))
