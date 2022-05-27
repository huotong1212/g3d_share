import asyncio
import sys


async def async_func_call(async_func, *args, **kwargs):
    """Calls a Pillar function.

    A semaphore is used to ensure that there won't be too many
    calls to Pillar simultaneously.
    """

    # partial = functools.partial(
    #     async_func, *args, **kwargs
    # )
    loop = asyncio.get_event_loop()

    # Python 3.8 deprecated the 'loop' parameter, 3.10 removed it.
    kwargs = {"loop": loop} if sys.version_info < (3, 8) else {}

    # Use explicit calls to acquire() and release() so that we have more control over
    # how long we wait and how we handle timeouts.
    # try:
    #     await asyncio.wait_for(pillar_semaphore.acquire(), timeout=10, **kwargs)
    # except asyncio.TimeoutError:
    #     log.info("Waiting for semaphore to call %s", pillar_func.__name__)
    #     try:
    #         await asyncio.wait_for(pillar_semaphore.acquire(), timeout=50, **kwargs)
    #     except asyncio.TimeoutError:
    #         raise RuntimeError("Timeout waiting for Pillar Semaphore!")
    return await loop.run_in_executor(None, async_func, *args)
    # try:
    #     return await loop.run_in_executor(None, partial)
    # finally:
    #     pillar_semaphore.release()
