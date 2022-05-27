import os

from . import appdirs


def get_user_cache_dir(username: str = "tourist") -> str:
    user_cache_dir = appdirs.user_cache_dir(appname="Blender", appauthor=False)
    cache_dir = os.path.join(user_cache_dir, "g3d", username, )

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir


def get_user_data_dir(username: str = "tourist") -> str:
    user_data_dir = appdirs.user_data_dir(appname="Blender", appauthor=False)
    data_dir = os.path.join(user_data_dir, "g3d", username, )

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir
