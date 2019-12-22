import asyncio


def handle_async(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    loop.create_task(func, *args, **kwargs)
    return fut