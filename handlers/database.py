# import pymysql
import aiomysql
import asyncio
import os
import tornado


def coroutine(func):
    func = asyncio.coroutine(func)

    def decorator(*args, **kwargs):
        future = tornado.concurrent.Future()

        def future_done(f):
            try:
                future.set_result(f.result())
            except Exception as e:
                future.set_exception(e)

        asyncio.async(func(*args, **kwargs)).add_done_callback(future_done)
        return future
    return decorator


conn_params = dict(host=os.getenv("DB_HOST", 'localhost'),
                   user=os.getenv("DB_USERNAME", 'root'),
                   password=os.getenv("DB_PASSWORD", ''),
                   db=os.getenv("DB_DATABASE", 'cgssh'),
                   cursorclass=aiomysql.DictCursor,
                   autocommit=True)


@asyncio.coroutine
def execute(sql, sql_args):
    global pool
    try:
        not pool
    except NameError:
        pool = yield from aiomysql.create_pool(**conn_params)
    with (yield from pool) as conn:
        cur = yield from conn.cursor()
        yield from cur.execute(sql, sql_args)
        result = yield from cur.fetchall()

    return result
