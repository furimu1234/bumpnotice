from discord.ext import commands as c
from asyncpgw import general

#pylint: disable=import-error
from utils import datas, embed, dget


bump = """bump(
    server bigint,
    notice boolean DEFAULT True
    enable boolean DEFAULT True,
    night_enable boolean DEFAULT True,
    mention boolean DEFAULT True,
    night_mention boolean DEFAULT True,
    role bigint,
    night_role bigint
)"""

class Notice(c.Cog, name='通知'):
    def __init__(self, bot):
        self.bot = bot
        self.dget = dget.Dget(bot)
        self.bump = general.Pg(bot, 'bump')

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


def setup(bot):
    bot.add_cog(Notice(bot))
    bot.add_table(bump)