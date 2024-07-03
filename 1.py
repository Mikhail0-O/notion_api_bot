import asyncio
from time import time


async def b(i):
    i.append(2)
    await asyncio.sleep(1)
    i.append(3)


async def a():
    i = [1]
    count = 0
    while count < 10:
        count += 1
        print(i)
        f = i.pop(0)
        task = asyncio.create_task(b(i))
        await task

start = time()
asyncio.run(a())
print(time() - start)


# def b(i):
#     i.append(2)
#     i.append(3)


# def a():
#     i = [1]
#     count = 0
#     while count < 10:
#         count += 1
#         print(i)
#         f = i.pop(0)
#         b(i)


# start = time()
# a()
# print(time() - start)
