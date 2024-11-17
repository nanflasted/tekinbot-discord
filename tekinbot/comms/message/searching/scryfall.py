import re

import requests
from discord import Colour
from discord import Embed
from discord.ext import commands


link_stem = 'https://api.scryfall.com/cards/named'
tekin_planeswalker = 'https://i.imgur.com/9agLW68.png'
scryfall_favicon = 'https://assets.scryfall.com/icon.png'
mtg_colours = {
    'W': Colour.from_rgb(248, 231, 185),  # '#F8E7B9',
    'U': Colour.from_rgb(179, 206, 234),  # '#B3CEEA',
    'B': Colour.from_rgb(166, 159, 157),  # '#A69F9D',
    'R': Colour.from_rgb(234, 159, 130),  # '#EA9F82',
    'G': Colour.from_rgb(196, 211, 202),  # '#C4D3CA',
    'C': Colour.from_rgb(255, 255, 255),  # '#FFFFFF',
}


def search(query, exact):
    search_payload = {"exact" if exact else "fuzzy": query}
    search_resp = requests.get(
        link_stem, params=search_payload
    )

    if search_resp.status_code == 404:
        return {'text': (
            'Can\'t find the said card, or there are multiple matches. '
            'Try to be more precise. Anyway, here is me in the Multiverse: '
            f'{tekin_planeswalker}'
        )}
    elif not search_resp.ok:
        return {'text': 'I can\'t into internetz'}

    try:
        resp = search_resp.json()

        colour = resp.get('color_identity')
        colour = 'C' if not colour else colour[0]

        attachment = Embed.from_dict({
            'author': {
                'name': 'Scryfall brought to you by Tekin',
                'url': 'https://www.scryfall.com/',
                'icon_url': scryfall_favicon,
            },
            'image': {
                'url': (
                    '{url}'.format(url=resp["image_uris"]["normal"])
                ) if resp["layout"] != "transform" else ('\n'.join([
                    face['image_uris']['normal'] for face in resp['card_faces']
                ]))
            },
            'color': mtg_colours[colour].value,
            'fields': [
                {
                    'name': 'Name',
                    'value': f'[{resp["name"]}]({resp["scryfall_uri"]})',
                    'inline': True
                },
                {'name': 'Mana', 'value': '{}'.format(
                    resp["mana_cost"] if resp['layout'] != 'transform' else (
                        ' // '.join([face['mana_cost']
                                     for face in resp['card_faces']])
                    )), 'inline': True},
                {'name': 'Type Line',
                    'value': f'{resp["type_line"]}', 'inline': True},
                {'name': 'Set', 'value': f'{resp["set"]}', 'inline': True},
                {'name': 'Text', 'value': '{}'.format(
                    resp['oracle_text'] if resp['layout'] == 'normal' else (
                        '\n'.join([face['oracle_text']
                                   for face in resp['card_faces']])
                    )
                )}
            ]
        })
        return attachment

    except Exception as e:
        print(e)
        return 'Can\'t find the said card.'


class ScryfallSearches(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def scryfall_callable(self, ctx, query, exact):
        result = search(query, exact)
        if isinstance(result, str):
            await ctx.send(content=result)
        else:
            await ctx.send(
                content='I did a scry 1 and topdecked:',
                embed=result
            )

    @commands.command(
        description="Tekin searches for a magic card.",
        help="""
        Usage: @TekinBot mtg [exactly] [card], or call via "[[cardname]]"
        Tekin will look up to scryfall for the MTG card and give relavant
        information about the card.
        If exactly parameter is specified, tekin will try to search directly
        for the name, otherwise Tekin will do a fuzzy search. Inline calls are
        always exact.
        """,
    )
    async def mtg(self, ctx, *cardname):
        exact = (cardname[0] == 'exactly')
        query = " ".join(cardname if not exact else cardname[1:])
        await self.scryfall_callable(ctx, query, exact)

    @commands.Cog.listener('on_message')
    async def mtg_inline(self, message):
        inline_rgx = r'^.*\[\[(?P<exact_bk>!)?(?P<query_bk>.*)\]\].*$'
        match = re.fullmatch(inline_rgx, message.content)
        if not match:
            return
        query = match.group('query_bk')
        exact = match.group('exact_bk')
        if not query:
            await message.channel.send('What exactly are you looking for?')
        await self.scryfall_callable(message.channel, query, exact)


async def setup(bot):
    await bot.add_cog(ScryfallSearches(bot))
