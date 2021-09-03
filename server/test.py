import asyncio
import aiopg
import pprint

dsn = 'dbname=aiopg user=aiopg password=password host=127.0.0.1'

async def go():
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 as test, 2 as blah")
                ret = []
                r = {}
                async for row in cur:
                    for i in range(0,len(cur.description)):
                        print(row[i], cur.description[i].name)
                    ret.append(row)
                assert ret == [(1,)]

loop = asyncio.get_event_loop()
loop.run_until_complete(go())
