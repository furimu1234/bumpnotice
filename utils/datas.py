import aiofiles, json

async def load():
    async with aiofiles.open('select.json') as f:
        data = await f.read()
        return json.loads(data)