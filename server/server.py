from aiohttp import web
import aiohttp_swagger
import uvloop
import aiopg
import asyncio
import argparse
import logging

loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)

parser = argparse.ArgumentParser(description="Simple crud restful service")

parser.add_argument('--db-host',
        help='Postgres host',
        default='127.0.0.1')

parser.add_argument('--loglevel',
        help='Event level to log http events',
        choices=('DEBUG','INFO','WARNING','ERROR','CRITICAL'),
        default='INFO')

columns = {'string','int','decimal'}

async def create(request):
    body = await request.json()
    if not set(body.keys()).issubset(columns):
        return web.json_response({'error':'invalid columnname'},status=400)

    async with request.app['database'].acquire() as conn:
        async with conn.cursor() as cur:
            cols = ','.join(body.keys())
            qmarks = ','.join(['%s'] * len(body.keys()))
            await cur.execute(
            """insert into objs ({}) 
            values ({})
            returning *;""".format(cols,qmarks),list(body.values()))
            ret = {}
            async for row in cur:
                for i in range(0,len(cur.description)):
                    ret[cur.description[i].name] = row[i]
            return web.json_response(ret)

async def read(request):
    async with request.app['database'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """select * 
                from objs 
                where obj_id = %s""",request.match_info['objId'])
            ret = {}
            async for row in cur:
                for i in range(0,len(cur.description)):
                    ret[cur.description[i].name] = row[i]
            return web.json_response(ret)

async def delete(request):
    async with request.app['database'].acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
            """delete from objs 
            where obj_id = %s
            RETURNING *;""",request.match_info['objId'])
            ret = {}
            async for row in cur:
                for i in range(0,len(cur.description)):
                    ret[cur.description[i].name] = row[i]
            return web.json_response(ret)

async def on_shutdown(app):
    print('Shutting down')
    app['database'].close()
    await app['database'].wait_closed()

async def init_app():
    app = web.Application()
    app.router.add_route('POST','/crud/',create)
    app.router.add_route('GET','/crud/{objId}',read)
    app.router.add_route('DELETE','/crud/{objId}',delete)
    dsn = 'dbname=aiopg user=aiopg password=password host={}'.format(args.db_host)

    app['database'] = await aiopg.create_pool(dsn)
    app.on_shutdown.append(on_shutdown)

    return app


if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging,args.loglevel))
    web.run_app(init_app())
