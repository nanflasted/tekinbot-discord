import re

from discord.ext import commands

from tekinbot.comms.message.searching import youtube


is_url = re.compile(
    r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?'
    r'[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
)


thread_theme_format = re.compile(
    r'.*\[Thread theme: (?P<theme>[^\]]*)\].*',
    flags=re.IGNORECASE
)


class ThreadTheme(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def check_current_topic_theme(self, syschan):
        if not syschan or not syschan.topic:
            return None
        current_topic = syschan.topic
        match = re.fullmatch(thread_theme_format, current_topic)
        if not match:
            return None
        return match.group('theme')

    async def replace_sys_chan_theme(self, syschan, theme):
        if not syschan:
            return
        current_topic_theme = self.check_current_topic_theme(syschan)
        current_topic = syschan.topic
        self.bot.theme = theme
        theme = theme or 'empty'
        if not current_topic_theme:
            await syschan.edit(
                topic=f'{current_topic} | [Thread theme: {theme}]'
            )
        else:
            await syschan.edit(
                topic=current_topic.replace(current_topic_theme, theme)
            )

    @commands.command(
        description="Tekin sets thread theme for the server.",
        help="""
        Usage: @TekinBot theme [theme]
        Tekin will add the theme to the system channel topic, and remember
        the thread theme.
        """
    )
    @commands.guild_only()
    async def theme(self, ctx, *, theme):
        prev_theme = self.check_current_topic_theme(
            ctx.guild.system_channel) or 'empty'
        if not re.fullmatch(is_url, theme):
            theme = youtube.search(theme, exact=True)[0]
        await ctx.send(f'thread theme was {prev_theme}, changed to {theme}')
        await self.replace_sys_chan_theme(ctx.guild.system_channel, theme)

    @commands.command(
        description="Tekin refutes the theme.",
        help="""
        Usage: @TekinBot refute [reason]
        Tekinbot will refute the current thread theme, clear it, and post the
        reason to the system channel.
        """
    )
    @commands.guild_only()
    async def refute(self, ctx, *, reason):
        syschan = ctx.guild.system_channel
        if not self.bot.theme:
            current_topic_theme = self.check_current_topic_theme(syschan)
            if not current_topic_theme:
                return await ctx.send('There was no theme.')

        await syschan.send(
            f'{ctx.author.mention} has refuted the current theme. \n'
            f'> {reason}'
        )
        await self.replace_sys_chan_theme(syschan, None)

    @commands.Cog.listener('on_message')
    async def post_theme(self, message):
        if not message.content.lower().startswith(
            f'{self.bot.user.mention} post me the thread theme'
        ):
            return
        current_topic_theme = self.bot.theme
        if not self.bot.theme:
            current_topic_theme = self.check_current_topic_theme(
                message.guild.system_channel
            )
            if current_topic_theme:
                self.bot.theme = current_topic_theme
            else:
                current_topic_theme = 'empty'
        await message.channel.send(f'Current theme is {current_topic_theme}')


def setup(bot):
    bot.add_cog(ThreadTheme(bot))
