import asyncio

def echo(s='pong'):
    return s


def mul2(a, b):
    return a * b

async def say_after(delay, what):
    await asyncio.sleep(delay)
    return what
