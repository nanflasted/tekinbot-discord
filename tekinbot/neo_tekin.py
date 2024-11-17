import argparse
import logging

from discord import Intents
from discord.ext import commands

import tekinbot.utils.db as du
from tekinbot.comms import tekin_extensions
from tekinbot.utils.config import tekin_secrets


log = logging.getLogger(__name__)


def tekin_args():
    parser = argparse.ArgumentParser(
        description='TekinBot Server'
    )
    parser.add_argument(
        '--dry-run', dest='dry_run', action='store_true',
        help=('set up Tekin for dry running; Tekin will print all '
              'posting actions to stdout, instead of sending Requests'
              ),
    )
    parser.add_argument(
        '--no-db', dest='nodb', action='store_true',
        help=('tekin will not read or write anything to database, '
              'everything will be performed either in a dry run fashion '
              'or in memory'
              ),
    )
    return parser.parse_args()


class TekinBot(commands.Bot):

    description = (
        "TaaD: Tekin (a knowledgeable and possibly friendly professor) "
        "as a DiscordBot"
    )

    def __init__(self, args):
        super().__init__(
            command_prefix=commands.when_mentioned,
            description=self.description,
            intents=Intents.all(),
        )
        # set up db here
        du.tekin_db_init(args.nodb)

        self.token = tekin_secrets('discord.bot_token')

        self.theme = None

        for ext in tekin_extensions:
            self.load_extension(ext)

    def run(self):
        super().run(self.token, reconnect=True)


if __name__ == '__main__':
    args = tekin_args()
    tekinbot = TekinBot(args)
    tekinbot.run()
