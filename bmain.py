from discord.ext import commands as c
from discord import Intents
from asyncpgw import general, start
from glob import glob

import os, traceback, asyncio

intent = Intents.all()


class Bumper_Main(c.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = 'b:',
            description = 'BUMPの通知をしたり、ランキングにしたりするBOT',
            intents=intent
        )

        self.tables = []


    async def ps_connect(self):
        self.pool = await start.connect(os.environ.get('BUMP_POSTG'))

    
    def add_table(self, table):
        if table not in self.tables:
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

        self.cog_load()

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