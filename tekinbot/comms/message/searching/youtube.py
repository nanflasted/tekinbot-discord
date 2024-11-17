import random
from operator import itemgetter

import requests
from bs4 import BeautifulSoup
from discord.ext import commands


res_stem = 'https://www.youtube.com/results'
link_stem = 'https://www.youtube.com{}'


def extract_search_res(parsed):

    return [
        t for t in map(itemgetter('href'), parsed.find_all(
            'a', attrs={"aria-hidden": "true"}
        )) if (
            (
                u'doubleclick' not in t
            ) and (
                u'watch' in t
            ) and (
                u'googleadservices' not in t
            )
        )
    ][:20]


def search(query, exact):
    search_payload = {'search_query': query.encode('utf-8')}
    search_resp = requests.get(res_stem, params=search_payload)

    if not search_resp.ok:
        return 'I can\'t into internetz', False
    parsed = BeautifulSoup(search_resp.text, "html.parser")

    # magic
    search_res = extract_search_res(parsed)
    if not search_res:
        return (
            'Somehow, I can\'t find anything; '
            'anyways, here\'s Wonderwall: '
            'https://www.youtube.com/watch?v=bx1Bh8ZvH84'
        ), False
    return link_stem.format(
        search_res[0] if exact else random.choice(search_res)
    ), True


class YoutubeSearches(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description="Tekin searches youtube given a keyword.",
        help="""
        Usage: @TekinBot youtube [exactly] keyword
        Tekinbot will search youtube with keyword, and return randomly one of
        the top 20 results. If "exactly" was specified, Tekin will always
        return the first result.
        """,
    )
    async def youtube(self, ctx, *keyword):
        exact = keyword[0] == 'exactly'
        query = " ".join(keyword if not exact else keyword[1:])
        query = query if query else ''
        await ctx.send(search(query, exact)[0])


async def setup(bot):
    await bot.add_cog(YoutubeSearches(bot))
