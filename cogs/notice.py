from discord.ext import commands as c
from discord.ext import tasks
from discord import Embed
from asyncpgw import general
from datetime import datetime, timedelta
from asyncio import TimeoutError

#pylint: disable=import-error
from utils import datas, embed, dget


bump = """bump(
    server bigint,
    notice boolean DEFAULT True,
    enable boolean DEFAULT True,
    night_enable boolean DEFAULT True,
    mention boolean DEFAULT True,
    night_mention boolean DEFAULT True,
    role bigint,
    night_role bigint,
    latest_time timestamp,
    channel bigint
)"""


BUMP_SUCCESS = 'https://images-ext-1.discordapp.net/external/tAuRcs-FCy2M8OaTS9Ims62J1vrFiviahjBDtpZrrBs/https/disboard.org/images/bot-command-image-bump.png'

#pylint: disable=no-member
class Notice(c.Cog, name='通知'):
    def __init__(self, bot):
        self.bot = bot
        self.dget = dget.Dget(bot)
        self.bump = general.Pg(bot, 'bump')
        self.time = general.Pg(bot, 'member_time')
        self.global_count = general.Pg(bot, 'global_count')
        self.count_ = general.Pg(bot, 'count')
        self.disboard = 302050872383242240

        self.check_bump.start()

    
    def cog_unload(self):
        self.check_bump.cancel()

    async def count(self, mes):
        if not (data := await self.global_count.fetch(member=mes.author.id)):
            await self.global_count.insert(member=mes.author.id)

            data = await self.global_count.fetch(member=mes.author.id)

        await self.global_count.update(count=data['count'] + 1, member=mes.author.id)

        if not (data_ := await self.count_.fetch(server=mes.guild.id, member=mes.author.id)):
            await self.count_.insert(server=mes.guild.id, member=mes.author.id)

            data_ = await self.count_.fetch(server=mes.guild.id, member=mes.author.id)

        await self.count_.update(count=data['count'] + 1, member=mes.author.id, server=mes.guild.id)

        return data['count'] + 1, data_['count'] + 1

        

    async def update_bump(self, ctx, menu, content):
        data = await self.bump.fetch(server=ctx.guild.id)

        enable = '有効' if data[content] else '無効'
        mes, reaction = await self.dget.check_reactions(ctx, f'現在の設定は`{enable}`になってるよ\nBUMPの感知を有効にする？')
        parms = {}
        parms[content] = True
        parms['server'] = ctx.guild.id
        if str(reaction.emoji) == '⭕':

            await self.bump.update(**parms)
        else:
            parms[content] = False
            await self.bump.update(**parms)

        await mes.add_reaction('\U00002705')

        default_mes, load_emoji = await embed.select(ctx, menu)
        return default_mes, load_emoji


    @c.command(aliases=['設定'])
    async def setting(self, ctx):
        """BUMPの設定をする
        
        設定項目: 感知の設定,通知設定,深夜の通知設定,メンション設定,深夜のメンション設定,通知する役職設定,深夜に通知する役職設定
        """

        guild = ctx.guild

        if not await self.bump.fetch(server=guild.id):
            await self.bump.insert(server=guild.id)

            e = embed.normal(
                title = '設定を新規保存したよ。設定を変更するにはもう一度コマンドを入力してね',
                desc = '・感知->有効\n・通知->有効\n・深夜通知->有効\n・メンション->有効\n・深夜メンション->有効\n・通知役職->未設定\n・深夜通知役職->未設定'
            )
            return await ctx.send(embed=e)

        d = await datas.load()
        default_mes, load_emoji = await embed.select(ctx, d['bump'])

        emoji = 0

        while emoji != 8:
            emoji = await self.dget.emoji_number(ctx, load_emoji)

            if emoji == 1:
                default_mes, load_emoji = await self.update_bump(ctx, d['bump'], 'notice')

            elif emoji == 2:
                default_mes, load_emoji = await self.update_bump(ctx, d['bump'], 'enable')

            elif emoji == 3:
                default_mes, load_emoji = await self.update_bump(ctx, d['bump'], 'night_enable')

            elif emoji == 4:
                default_mes, load_emoji = await self.update_bump(ctx, d['bump'], 'mention')
            
            elif emoji == 5:
                default_mes, load_emoji = await self.update_bump(ctx, d['bump'], 'night_mention')

            elif emoji == 6:
                role = await self.dget.role(ctx, 'BUMPを通知する役職を入力してね')

                if role is None:
                    e = embed.error('役職が見つからなかったよ')
                    return await ctx.send(embed=e)

                await self.bump.update(role=role.id, server=guild.id)

            elif emoji == 7:
                role = await self.dget.role(ctx, 'BUMPを深夜に通知する役職を入力してね')

                if role is None:
                    e = embed.error('役職が見つからなかったよ')
                    return await ctx.send(embed=e)

                await self.bump.update(night_role=role.id, server=guild.id)

        await default_mes.remove_reaction(load_emoji, self.bot.user)
        e = embed.succes(desc='保存に成功したよ！')
        return await ctx.send(embed=e)


    @c.Cog.listener()
    async def on_message(self, mes_bot):

        notice_now = datetime.now()

        if await mes_bot.channel.history(limit=3).get(author__id=self.bot.user.id):
            if mes_bot.author.id != self.bot.user.id:
                return
            if not mes_bot.embeds:
                return
            for e in mes_bot.embeds:
                if e.title == Embed.Empty:
                    return
                
                if 'ランキングにチャレンジ！' not in e.title:
                    return

        def mes_check(m):
            return not m.author.bot and m.channel == mes_bot.channel and m.content == '!d bump'

        try:
            mes = await self.bot.wait_for('message', check=mes_check, timeout=60)
        except TimeoutError:
            return

        if not await self.bump.fetch(server=mes.guild.id, notice=True):
            return
        
        def check(m):
            return m.author.id == self.disboard and m.channel == mes.channel

        try:
            m = await self.bot.wait_for('message', check=check, timeout=60)
        except TimeoutError:
            return

        if m.author.id != self.disboard:
            return

        if not (embed := m.embeds):
            return

        for e in embed:
            if e.image.proxy_url != BUMP_SUCCESS:
                return

        await self.bump.update(latest_time=datetime.now() + timedelta(hours=2), server=mes.guild.id)
        await self.bump.update(channel=mes.channel.id, server=mes.guild.id)

        now = notice_now - datetime.now()
        
        if not await self.time.fetch(member=mes.author.id):
            await self.time.insert(memebr=mes.author.id)

        await self.time.update(latest_time=now, member=mes.author.id)

        global_count, server_count = await self.count(mes)

        data = await self.time.fetch(member=mes.author.id)

        global_datas = await self.time.sort_not_column_fetchs('latest_time', limit=None)

        server_datas = [data for data in global_datas if mes.guild.get_member(data['member'])]

        data = await self.time.fetch(member=mes.author.id)

        global_rank = global_datas.index(data)

        server_rank = server_datas.index(data)

        e = embed.normal(
            title = f'BUMPを検知!ランキングに反映!',
            url = f'https://disboard.org/ja/server/{mes.guild.id}',
            description = f'BOTの通知が出てからBUMPした時間: {now}\n'\
                f'サーバーランキング: {server_rank}位\n'\
                f'グローバルランキング: {global_rank}位\n'\
                f'貴方がBUMPした回数: {global_count} \n'\
                f'貴方がこのサーバーでBUMPした回数: {server_count}'
        )
        await mes.channel.send(embed=e)

    def times(self, timestamp):
        d = timestamp.strftime('%d')
        h = timestamp.strftime('%H')
        m = timestamp.strftime('%M')
        s = timestamp.strftime('%S')

        return d, h, m, s


    @tasks.loop(seconds=1)
    async def check_bump(self):
        await self.bot.wait_until_ready()
        now = datetime.now()

        for guild in self.bot.guilds:

            role = None

            if not (data := await self.bump.fetch(server=guild.id)): continue

            if not (channel := guild.get_channel(data['channel'])): continue
            
            if now.strftime('%H') in ['00', '01', '02', '03', '04', '05', '06']:
                if not data['night_enable']: continue
                
                if data['night_mention']:
                    role = guild.get_role(data['night_role'])

            else:
                if not data['enable']: continue

                if data['mention']:
                    role = guild.get_role(data['role'])
     
            data_day, data_hour, data_minute, data_second = self.times(data['latest_time'])
            day, hour, minute, second= self.times(now)

            if data_day != day: continue
            if data_hour != hour: continue
            if data_minute != minute: continue
            if data_second != second: continue

            e = embed.normal(
                title = 'BUMPできるよ！ランキングにチャレンジ！',
            )

            if not role:
                await channel.send(embed=e)
            else:
                await channel.send(role.mention, embed=e)
                        


def setup(bot):
    bot.add_cog(Notice(bot))
    bot.add_table(bump)