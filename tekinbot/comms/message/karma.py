import re
import shlex
import typing

import discord
from discord.ext import commands

from tekinbot.db.models.karma import Karma
from tekinbot.utils.db import get_session


comm_re = re.compile(r'(?P<target>.*)(\+\+|--)', flags=re.IGNORECASE)

resp_tmpl = '{} has a karma of {}, and gave out {} amount of karma.'


def self_inc_check(match, request):
    return match.group('target') == f"<@{request['event']['user']}>"


class KarmaKeeper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description="Tekin looks up someone or something's karma count",
        help="""
        Usage: @TekinBot karma target or @TekinBot karma "long target"

        Tekin searches the database for the target's karma, along with how
        much karma the target has sent out. If target's name is more than one
        word separated by space, it needs to be quoted with double quotes.

        Karma can be given via `target++` or `target--`, or similarly,
        `"long target"++` or `"long target"-- for targets with more than one
        word. Alternatively, you may react to a message with :upvote: or
        :downvote:
        """
    )
    async def karma(
        self, ctx,
        target: typing.Union[commands.UserConverter, str]
    ):
        if isinstance(target, discord.user.BaseUser):
            user = str(target.id)
            mention = target.mention
        else:
            user = mention = target

        sesh = get_session()
        qres = sesh.query(Karma).filter_by(user=user)
        await ctx.send(
            resp_tmpl.format(mention, 0, 0) if not qres.count() else (
                resp_tmpl.format(
                    mention, qres.value('received'), qres.value('sent'))
            )
        )
        sesh.close()

    async def karma_inc_callable(self, ctx, author, src_count, ledger):
        # get a db session
        sesh = get_session()
        try:
            # update the database for each user/change pair in the ledger
            for user, delta in ledger.items():
                qres = sesh.query(Karma).filter_by(user=user)
                if not qres.count():
                    sesh.add(Karma(user=user, sent=0, received=delta))
                else:
                    qres.update({'received': Karma.received + delta})

            # update the database for the source user
            qres = sesh.query(Karma).filter_by(user=author.name)
            if not qres.count():
                sesh.add(Karma(user=author.name, sent=src_count, received=0))
            else:
                qres.update({'sent': Karma.sent + src_count})

            # commit our changes to the database
            sesh.commit()
        except Exception as e:
            raise e
            sesh.rollback()
        finally:
            sesh.close()

    @commands.Cog.listener('on_message')
    async def karma_message_inc(self, message):
        if not ('++' in message.content or '--' in message.content):
            return
        # parse all mentions and remove the space after mentions if there are
        # any
        sentence = message.content
        for u in message.mentions:
            sentence = sentence.replace(f'{u.mention} ', f'{u.id}')
            sentence = sentence.replace(f'{u.mention}', f'{u.id}')

        # tokenize the sentence into words and quoted phrases
        tokens = shlex.split(sentence)

        # parse each token for ++/--s
        matches = [re.match(
            r'(?P<target>.+?)(?P<inc>(\+\+|--))', t
        ) for t in tokens]

        # filter out matches for the source user
        matches = [
            m for m in matches if (
                m is not None
            ) and (
                m.group('target') != message.author.mention
            )
        ]

        src = 0
        ledger = {}
        for m in matches:
            d = 1 if m.group('inc') == '++' else -1
            src += d
            ledger[m.group('target')] = (
                d if m.group('target') not in ledger else
                ledger[m.group('target')] + d
            )

        await self.karma_inc_callable(
            message.channel, message.author, src, ledger
        )


async def setup(bot):
    await bot.add_cog(KarmaKeeper(bot))
