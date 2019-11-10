import functools

import wikipedia
from discord.ext import commands
from wikipedia import DisambiguationError
from wiktionaryparser import WiktionaryParser


@functools.lru_cache()
def cached_wikipedia(message):
    try:
        return wikipedia.page(message), []
    except DisambiguationError as e:
        return wikipedia.page(e.options[0]), e.options[1:]


class WikiSearches(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.wiktionary = WiktionaryParser()

    async def wiki_callable(self, ctx, message):
        if not wikipedia.search(message):
            return await ctx.send(
                f'I can\'t possibly know what {message} is'
            )

        page, disambi = cached_wikipedia(message)
        if len(disambi) > 5:
            disambi = disambi[:4]
        disambi = '' if not disambi else ', '.join(
            disambi[:-1]) + ' or ' + disambi[-1]
        summary = page.summary.split('. ')[0]
        if not disambi:
            await ctx.send(f'{summary}, see {page.url} for more')
        else:
            await ctx.send(
                f'assuming {message} means {page.title}, {summary}\n'
                f'see {page.url} for more\n'
                f'try asking about {disambi} if that\'s not it'
            )

    @commands.command(
        description="Tekin looks up things on Wikipedia.",
        help="""
        Usage: @TekinBot [wiki] [thing] or @TekinBot [what|who] is [thing]
        Tekin searches wikipedia for thing, and gives the result from the
        first disambiguation, if applicable.
        """
    )
    async def wiki(self, ctx, *, message):
        await self.wiki_callable(ctx, message)

    @commands.Cog.listener('on_message')
    async def what_is(self, message):
        """workaround since aliases for commands can't contain spaces"""
        prefixes = [
            f'{self.bot.user.mention} what is ',
            f'{self.bot.user.mention} who is ',
        ]
        for p in prefixes:
            if message.content.lower().startswith(p):
                content = message.content.lower().replace(p, '')
                if content.endswith('thread theme'):
                    return await message.channel.send(
                        f"Current theme is {self.bot.theme or ''}"
                    )
                await self.wiki_callable(
                    ctx=message.channel,
                    message=content,
                )

    @commands.command(
        description="Tekin looks up the Wiktionary.",
        help="""
        Usage: @TekinBot define [word]
        Tekin looks up the wiktionary for word, and try to parse and return
        its definition.
        """,
    )
    async def define(self, ctx, word):
        entry = self.wiktionary.fetch(word)

        if not entry:
            return await ctx.send(f'Not sure how to define {word}')
        else:
            entry = entry[0]
        # the wiktionary parser has some problems in parsing the definitions
        # change this part after submitting the pull request

        # split(\n)[0] will always be the tense/form of the word
        # e.g. and etc. mess with the split('.') so we take em out,
        # since we don't need what's after anyways
        defs = [d['text'][1] for d in entry['definitions']]
        extra = '' if len(defs) <= 1 else '\n* '.join([''] + defs[1:])
        await ctx.send(
            f'{word} usually means\n'
            f'* {defs[0]}'
            f'{extra}'
        )


def setup(bot):
    bot.add_cog(WikiSearches(bot))
