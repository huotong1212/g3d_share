import asyncio
import functools
import os
import pickle
import sys
from datetime import datetime, timedelta

import bpy
import requests

from . import async_loop
from . import log
from . import routers
from . import status
from . import utils
from .errors import STSGetFailedError
from .utils import get_user_cache_dir


class AuthToken(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    # 该操作类的唯一ID，供其他类进行调用
    bl_idname = 'objects.auth_token'
    # 在operator操作中显示的名字
    bl_label = "获取用户Token"
    bl_description = "获取用户Token"
    bl_options = {'REGISTER', 'UNDO'}

    G3D_SERVER_URL = "https://aiedit3d.com"

    # 必须要实现的父类的接口
    async def async_execute(self, context):
        """
        登录获取token
        """

        url = self.G3D_SERVER_URL + "/api/user/customer_email_login/"
        data = {
            "email": "lukedunphy@foxmail.com",
            "password": "abc@12399",
        }
        response = requests.post(url, data)
        if response.status_code == 200:
            return response.json()
        else:
            return None


def get_sts_token() -> dict:
    response = routers.get_sts_token()
    if response.status_code != status.HTTP_200_OK:
        raise STSGetFailedError()
    data = response.json()["data"]
    # 设置过期时间
    data["Expiration"] = datetime.now() + timedelta(minutes=50)
    return data


def pickle_sts_token(user_cache_dir: str, data: dict):
    with open(os.path.join(user_cache_dir, "sts.pickle"), mode="wb") as wf:
        pickle.dump(data, wf, pickle.HIGHEST_PROTOCOL)


async def async_pickle_sts_token(user_cache_dir: str, data: dict):
    with open(os.path.join(user_cache_dir, "sts.pickle"), mode="wb") as wf:
        pickle.dump(data, wf, pickle.HIGHEST_PROTOCOL)


def check_sts_token() -> dict:
    user_cache_dir = get_user_cache_dir()
    pickle_path = os.path.join(user_cache_dir, "sts.pickle")
    if not os.path.exists(pickle_path):
        data = get_sts_token()
        pickle_sts_token(user_cache_dir, data)

    with open(pickle_path, mode="rb") as f:
        ret = pickle.load(f)
        expiration = ret["Expiration"]
        if expiration < datetime.now():
            # 已过期，重新获取
            res = get_sts_token()
            return res
        else:
            return ret


class AliSTS(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    # 该操作类的唯一ID，供其他类进行调用
    bl_idname = 'objects.sts_token'
    # 在operator操作中显示的名字
    bl_label = "获取阿里云OSS临时STS"
    bl_description = "获取阿里云OSS临时STS"
    bl_options = {'REGISTER', 'UNDO'}

    # 必须要实现的父类的接口
    async def async_execute(self, context):
        """
        登录获取token
        """
        data = await get_sts_token()
        user_cache_dir = utils.get_user_cache_dir()
        log.info("user_cache_dir:", user_cache_dir)
        await async_pickle_sts_token(user_cache_dir, data)


async def async_func_call(async_func, *args, **kwargs):
    """Calls a Pillar function.

    A semaphore is used to ensure that there won't be too many
    calls to Pillar simultaneously.
    """

    partial = functools.partial(
        async_func, *args, **kwargs
    )
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
    return await loop.run_in_executor(None, partial)
    # try:
    #     return await loop.run_in_executor(None, partial)
    # finally:
    #     pillar_semaphore.release()


def register():
    bpy.utils.register_class(AliSTS)


def unregister():
    bpy.utils.unregister_class(AliSTS)
