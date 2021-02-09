from discord.ext import commands as c
from discord import Embed, utils
from attrdict import AttrDict
from asyncio import TimeoutError

class Dget:
    def __init__(self, bot):
        self.bot = bot


    async def text_channel(self, ctx, description=None):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        desc = description or '指定するチャンネルを入力してね'

        await ctx.send(desc.replace('チャンネル', 'テキストチャンネルの名前・ID・メンション'))


        get_channel = await self.bot.wait_for('message', check=check)

        try:
            channel = await c.TextChannelConverter().convert(ctx, get_channel.content)
            return channel
        except c.errors.ChannelNotFound:
            return None


    async def voice_channel(self, ctx, description=None):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        desc = description or '指定するチャンネルを入力してね'

        await ctx.send(desc.replace('チャンネル', 'ボイスチャンネルの名前・ID・メンション'))

        get_channel = await self.bot.wait_for('message', check=check)

        try:
            channel = await c.VoiceChannelConverter().convert(ctx, get_channel.content)
            return channel
        except c.errors.ChannelNotFound:
            return None


    async def category_channel(self, ctx, description=None):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        desc = description or '指定するチャンネルを入力してね'

        await ctx.send(desc.replace('チャンネル', 'カテゴリーチャンネルの名前・ID・メンション'))

        get_channel = await self.bot.wait_for('message', check=check)

        try:
            channel = await c.CategoryChannelConverter().convert(ctx, get_channel.content)
            return channel
        except c.errors.ChannelNotFound:
            return None

    async def role(self, ctx, description=None):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        desc = description or "指定する役職を入力してね"

        await ctx.send(desc.replace('役職', '役職の名前・ID・メンション'))

        get_role = await self.bot.wait_for('message', check=check)

        try:
            role = await c.RoleConverter().convert(ctx, get_role.content)
            return role
        except c.errors.RoleNotFound:
            if len(get_role.raw_role_mentions) == 0:
                return None
            else:
                return get_role.raw_role_mentions

    async def member(self, ctx, name, description=None):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        desc = description or '指定するメンバーを入力してね'

        await ctx.send(desc.replace('メンバー', 'メンバーの名前・4桁・ID・メンション'))

        get_member = await self.bot.wai_for('message', check=check)

        try:
            return await c.MemberConverter().convert(ctx, get_member.content)

        except c.errors.MemberNotFound:
            from difflib import SequenceMatcher
            #類似度が0.2以上だったらリストに入れる
            members = [member for member in ctx.guild.members if SequenceMatcher(None, get_member.content, str(member)).quick_ratio() >= 0.2]

            if members != []:
                if len(members) == 1:
                    return members[0]
                else:
                    e = Embed(
                        description = '\n'.join(f'{i}: {member}' for i, member in enumerate(members, 1))
                    )
                    await ctx.send(embed=e)
                    mes = await self.get_mes(ctx, '上記の中から番号を入力してね')
                    try:
                        number = int(mes.content) - 1
                    except ValueError:
                        return
                    return members[number]
            else:
                return


    async def get_mes(self, ctx, desc):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(desc)

        m = await self.bot.wait_for('message', check=check)
        return m


    async def emoji_number(self, ctx, mes):
        def check(r, u):
            return ctx.author == u

        load_emoji = ctx.bot.get_emoji(773858253884227594)

        try:
            r, _u = await self.bot.wait_for('reaction_add', check=check, timeout=180)
        except TimeoutError:
            await mes.remove_reaction(load_emoji, self.bot.user)
            return None

        e = str(r.emoji)
        es = list(e)
        
        try:
            emoji = int(es[0])
            return emoji
        except ValueError:
            await mes.remove_reaction(load_emoji, self.bot.user)
            return None


    async def check_reactions(self, ctx, description):
        def react_check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⭕', '❌']

        e = Embed(
            description=description
        )
        e.set_author(name='`⭕❌`で選択してね')
        m = await ctx.send(embed=e)
        await m.add_reaction("⭕")
        await m.add_reaction('❌')

        reaction, _user = await self.bot.wait_for('reaction_add', check=react_check)

        return m, reaction






    def ids(self):
        return AttrDict({
            "server": {
                "main": 754680802578792498
            },
            "channels": {
                "male": 767307773553672212,
                "female": 767307843056435240,
                "profile_notice": 773204984899829760,
                "server_update": 767375108636934184,
                "bot_update": 767375135547064381,
                "greeting": 767339917659209761,
                "err": 754710116753997876,
                "paid": 764394104431181824,
                "open_ban": 767404090908475432
            },
            "roles": {
                "male": 755080619637080225,
                "female": 755087406335524945,
                "not_profile": 767337793504280637,
                "greeting": 767340587162402818
            }
        })
            