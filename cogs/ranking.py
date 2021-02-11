from discord.ext import commands as c
from discord import Color
from asyncpgw import general
from asyncio import gather, TimeoutError


#pylint: disable=import-error
from utils import embed


member_time = """ member_time(
    member bigint,
    latest_time timestamp
)"""

global_count = """global_count(
    member bigint,
    count bigint DEFAULT 0
)"""

count = """count(
    server bigint,
    member bigint,
    count bigint DEFAULT 0
)"""


class Ranking(c.Cog, name='ランキング'):
    def __init__(self, bot):
        self.bot = bot
        self.times = general.Pg(bot, 'member_time')
        self.global_counts = general.Pg(bot, 'global_count')
        self.counts = general.Pg(bot, 'count')
        self.contents = ['グローバルランキング', 'サーバーランキング']

        self.emojis = {
            "first": "\U000023ee",
            "back": "\U000023ea",
            "next": "\U000023e9",
            "last": "\U000023ed"
        }

        self.pages = {
            'first': 1,
            'last': len(self.contents)
        }

    
    async def datas(self, data_opt='time'):
        datas = {
            'time': await self.times.sort_not_column_fetchs('latest_time', 'ASC', limit=30),
            'global_count': await self.global_counts.sort_not_column_fetchs('count', 'DESC', limit=30),
            'server_count': await self.counts.sort_not_column_fetchs('count', 'DESC', limit=30)
        }

        return datas.get(data_opt)

    
    async def refresh(self, guild, data_opt='time'):
        not_members = ['a']

        sort_datas = await self.datas(data_opt)
        
        while not_members != []:
            not_members = [data for data in sort_datas if not guild.get_member(data["member"])]

            if not_members != []:
                gather(*[self.times.delete(**dict(data)) for data in not_members])

                sort_datas = await self.datas(data_opt)

        return sort_datas


    async def global_ranking(self, ctx):
        guild = ctx.guild

        if not (sort_datas := await self.times.sort_not_column_fetchs('latest_time', 'ASC', limit=30)):
            e = embed.normal(
                title = 'このBOTが動いてからまだBUMPが行われていないよ!',
                description = f'[こちら](https://disboard.org/dashboard)からDISBOARDを自分のサーバーに招待してかBUMPをして、もう一度コマンド打ってね!'
            )
            return e

        sort_datas = await self.refresh(guild)

        datas = [f'{self.bot.get_user(data["member"])}: {data["latest_time"]}' for data in sort_datas if not self.bot.get_user(data["member"])]

        if not (user_data := await self.times.fetch(memebr=ctx.author.id)):
            rank = '貴方はまだBUMPをしてないよ!'
        else:
            rank = datas.index(user_data)

        e = embed.normal(
            title = f'BUMPランキング | 上位30人',
            description='\n'.join(data for data in datas)
        )
        e.add_field(
            name = '貴方の順位',
            value = f'{rank}'
        )
        e.set_author(name=1)
        e.set_footer(text='下のリアクションを押すと次のランキングに切り替わるよ')
        return e
    

    async def server_ranking(self, ctx):
        guild = ctx.guild
        if not (sort_datas := await self.times.sort_not_column_fetchs('latest_time', 'ASC', limit=30)):
            e = embed.normal(
                title = 'このサーバーではまだBUMPが行われていないよ!',
                description = f'[こちら](https://disboard.org/dashboard)からDISBOARDを自分のサーバーに招待してかBUMPをして、もう一度コマンド打ってね!'
            )
            return e
        
        sort_datas = await self.refresh(guild)
        
        datas = [data for data in sort_datas if guild.get_member(data["member"])]

        if not (user_data := await self.times.fetch(memebr=ctx.author.id)):
            rank = '貴方はまだBUMPをしてないよ!'
        else:
            rank = datas.index(user_data)

        e = embed.normal(
            title = f'{guild}のBUMPランキング | 上位30人',
            description='\n'.join(f'{guild.get_member(data["member"]).mention}: {data["latest_time"]}' for data in datas)
        )
        e.add_field(
            name = '貴方の順位',
            value = f'{rank}'
        )
        e.set_author(name=2)
        e.set_footer(text='下のリアクションを押すと次のランキングに切り替わるよ')
        return e


    async def global_count(self, ctx):
        guild = ctx.guild

        if not (sort_datas := await self.global_counts.sort_not_column_fetchs('count', limit=30)):
            e = embed.normal(
                title = 'このBOTが動いてからまだBUMPが行われていないよ!',
                description = f'[こちら](https://disboard.org/dashboard)からDISBOARDを自分のサーバーに招待してかBUMPをして、もう一度コマンド打ってね!'
            )
            return e

        sort_datas = await self.refresh(guild, 'global_count',)

        datas = [f'{self.bot.get_user(data["member"])}: {data["count"]}' for data in sort_datas if not self.bot.get_user(data["member"])]

        if not (user_data := await self.times.fetch(memebr=ctx.author.id)):
            rank = '貴方はまだBUMPをしてないよ!'
        else:
            rank = datas.index(user_data)

        e = embed.normal(
            title = f'BUMPランキング | 上位30人',
            description='\n'.join(data for data in datas)
        )
        e.add_field(
            name = '貴方の順位',
            value = f'{rank}'
        )
        e.set_author(name=1)
        e.set_footer(text='下のリアクションを押すと次のランキングに切り替わるよ')
        return e


    async def server_count(self, ctx):
        guild = ctx.guild

        if not (sort_datas := await self.counts.sort_not_column_fetchs('count', limit=30)):
            e = embed.normal(
                title = 'このBOTが動いてからまだBUMPが行われていないよ!',
                description = f'[こちら](https://disboard.org/dashboard)からDISBOARDを自分のサーバーに招待してかBUMPをして、もう一度コマンド打ってね!'
            )
            return e

        sort_datas = await self.refresh(guild, 'server_count',)

        datas = [f'{self.bot.get_user(data["member"])}: {data["count"]}' for data in sort_datas if not self.bot.get_user(data["member"])]

        if not (user_data := await self.times.fetch(memebr=ctx.author.id)):
            rank = '貴方はまだBUMPをしてないよ!'
        else:
            rank = datas.index(user_data)

        e = embed.normal(
            title = f'BUMPランキング | 上位30人',
            description='\n'.join(data for data in datas)
        )
        e.add_field(
            name = '貴方の順位',
            value = f'{rank}'
        )
        e.set_author(name=1)
        e.set_footer(text='下のリアクションを押すと次のランキングに切り替わるよ')
        return e


    @c.command(aliases=['ranking', 'ランク', 'ランキング', 'らんく', 'らんきんぐ'])
    async def rank(self, ctx):
        """BUMPのランキングを表示"""

        contents = ['global', 'server']

        emojis = [f'{i}\U0000fe0f\U000020e3' for i in range(1, len(contents) + 1)]

        def check(react, user):
            return ctx.author.id == user.id and str(react.emoji) in emojis

        e = await self.global_ranking(ctx)
        mes = await ctx.send(embed=e)
        for emoji in self.emojis.values():
            await mes.add_reaction(emoji)

        while True:
            try:
                react, _user = await self.bot.wait_for('reaction_add', check=check, timeout=600)
            except TimeoutError: return

            if str(react.emoji) == self.emojis.get('next'):
                author_name = int(e.author.name)
                next_page = author_name if author_name != self.pages.get('last') else 1

                if next_page == 1:
                    e = await self.global_ranking(ctx)
                elif next_page == 2:
                    e = await self.server_ranking(ctx)

                else: continue

                await mes.edit(embed=e)

            elif str(react.emoji) == self.emojis.get('back'):
                author_name = int(e.author.name)
                next_page = author_name if author_name != self.pages.get('first') else self.pages.get('last')

                if next_page == 1:
                    e = await self.global_ranking(ctx)
                elif next_page == 2:
                    e = await self.server_ranking(ctx)

                else: continue

                await mes.edit(embed=e)

            elif str(react.emoji) == self.emojis.get('first'):
                e = await self.global_ranking(ctx)

                await mes.edit(embed=e)

            elif str(react.emoji) == self.emojis.get('last'):
                e = await self.server_ranking(ctx)

                await mes.edit(embed=e)


def setup(bot):
    bot.add_cog(Ranking(bot))
    bot.add_table(member_time)
    bot.add_table(global_count)
    bot.add_table(count)