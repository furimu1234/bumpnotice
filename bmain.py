from discord.ext import commands as c
from discord import Intents
from asyncpgw import general, start
from glob import glob

import os, traceback, asyncio

intent = Intents.all()


class Bumper_Main(c.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = None,
            description = 'BUMPの通知をしたり、ランキングにしたりするBOT',
            intents=intent
        )

        self.tables = []

        prefix_table = """
            server bigint,
            prefixes text[]  DEFAULT array[] :: text[]
        """

        self.add_table(prefix_table)


    async def prefix_callble(self, bot, mes):
        guild = mes.guild

        if not guild:
            return 'b:'

        prefix = general.Pg(self, 'prefix')

        if not (prefixes := await prefix.fetch(server=guild.id)):
            await prefix.insert(server=guild.id)
            await prefix.add(prefixes='b:', server=guild.id)
            return 'b:'

        return prefixes['prefixes']


    async def ps_connect(self):
        self.pool = await start.connect(os.environ.get('BUMP_POSTG'))

    
    def add_table(self, table):
        if table in self.tables:
            self.tables.append(table)


    def cog_load(self):
        default_files = glob('cogs/*.py')

        for file in default_files:
            file_name = file.replace('.py', '').replace('/', '.')

            if not file_name.islower():
                continue
            try:
                self.load_extension(file_name)
            except c.errors.NoEntryPointError:
                continue
            except c.errors.ExtensionAlreadyLoaded:
                self.reload_extension(file_name)


        files = glob("cogs/**/*.py")

        for file in files:
            file_name = file.replace('.py', '').replace('/', '.')

            if not file_name.islower():
                continue

            try:
                self.load_extension(file_name)
            except c.errors.NoEntryPointError:
                continue
            except c.errors.ExtensionAlreadyLoaded:
                self.reload_extension(file_name)
            except:
                print(traceback.format_exc())


    async def on_ready(self):
        print('起動しました')

        for table in self.tables:
            await start.create(self.pool, table)

    
    async def start(self):
        await super().start(os.environ.get('B_TOKEN'))

    
    def main(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.ps_connect())
        loop.run_until_complete(self.start())
        loop.close()


if __name__ == '__main__':
    bot = Bumper_Main()
    bot.main()