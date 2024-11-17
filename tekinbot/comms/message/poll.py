import asyncio

from discord.ext import commands


class Polling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.emotes = [
            '{}\u20e3'.format(x) for x in range(10)
        ]
        self.polls = {}

    async def count_poll(self, ctx, poll):
        winner = set()
        maxc = 0
        print(poll['counts'])
        for o, c in poll['counts'].items():
            if c > maxc:
                winner = set([o])
                maxc = c
            if c == maxc:
                winner.add(o)

        await ctx.send(
            f'{ctx.author.mention}\'s poll {poll["id"]} has ended!\n'
            f'> {poll["question"]}\n'
            f'The result is: {winner} with a count of {maxc}! '
            f'Thanks for participating.'
        )

    @commands.command(
        description="Tekin starts a poll for your question",
        help="""
        Usage: @TekinBot poll "question" "option 1" ["option 2"] ...
        Tekin will start a poll, and assign an emote to each option. Other
        users may react to the poll with the emote to participate in the poll,
        and after a set period of time the poll closes, and Tekin announces the
        result.
        You may supply at most 10 options.
        """,
    )
    @commands.guild_only()
    async def poll(self, ctx, question, *options):
        if not question:
            return await ctx.send('Can\'t poll without a topic...')
        if not options or len(options) < 1:
            return await ctx.send('Can\'t poll without an option...')

        options = list(set(options))

        if len(options) > 10:
            return await ctx.send('too many options, too little time')

        poll_text = (
            f'Calling for votes! {ctx.author.mention} is asking:\n'
            f'> {question} \n'
        )

        emote_to_options = {
            self.emotes[i]: options[i] for i in range(len(options))
        }

        poll_text = poll_text + '\n'.join(
            '{}: {}'.format(e, o) for e, o in emote_to_options.items()
        )

        poll = await ctx.send(poll_text)
        await ctx.send(
            f'{ctx.author.mention}, your poll is {poll.id}, it will '
            f'automatically end in 30 mins. You may invoke `@TekinBot endpoll '
            f'{poll.id}` to end it early.'
        )

        for i in range(len(options)):
            await poll.add_reaction(self.emotes[i])

        self.polls[poll.id] = {
            'id': poll.id,
            'question': question,
            'author': ctx.author,
            'counts': {
                o: 0 for o in options
            },
            'emotes': emote_to_options,
        }

        await asyncio.sleep(1800)

        poll = self.polls.pop(poll.id, None)
        if not poll:
            return
        else:
            await self.count_poll(ctx, poll)

    @commands.command(
        hidden=True
    )
    @commands.guild_only()
    async def endpoll(self, ctx, poll_id: int):
        poll = self.polls.get(poll_id, None)
        if not poll:
            return await ctx.send(f'poll {poll_id} doesn\'t exist!')
        op = poll.get('author')
        if ctx.author != op:
            return await ctx.send(
                f'This was not your poll, {ctx.author.mention}, you may not '
                f'end it early.'
            )
        poll = self.polls.pop(poll_id)
        await self.count_poll(ctx, poll)

    @commands.Cog.listener('on_reaction_add')
    async def poll_vote(self, reaction, user):
        if user == self.bot.user:
            return
        if reaction.message.id in self.polls:
            poll = self.polls[reaction.message.id]
            poll['counts'][poll['emotes'][reaction.emoji]] += 1
        else:
            return

    @commands.Cog.listener('on_reaction_remove')
    async def poll_unvote(self, reaction, user):
        if user == self.bot.user:
            return
        if reaction.message.id in self.polls:
            poll = self.polls[reaction.message.id]
            poll['counts'][poll['emotes'][reaction.emoji]] -= 1
        else:
            return


async def setup(bot):
    await bot.add_cog(Polling(bot))
