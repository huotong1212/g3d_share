# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "G3dShare",
    "author": "",
    "description": "",
    "blender": (3, 1, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}
import logging
import os
from . import addon_updater_ops

def install_oss2():
    print('Run child process  (%s)...' % (os.getpid()))
    import pip
    pip.main(["install", "oss2"])
    print("oss2 installed successfully")

# Support reloading
if "pillar" in locals():
    import importlib

    wheels = importlib.reload(wheels)
    wheels.load_wheels()

    pillar = importlib.reload(pillar)
    cache = importlib.reload(cache)
else:
    from . import wheels

    wheels.load_wheels()

log = logging.getLogger(__name__)


def register():
    addon_updater_ops.register(bl_info)


    """Late-loads and registers the Blender-dependent submodules."""
    try:
        import oss2
    except ModuleNotFoundError:
        from multiprocessing import Process
        p = Process(target=install_oss2, args=())
        print('Child process will start.')
        p.start()
        p.join()

    import sys

    _monkey_patch_requests()

    # Support reloading
    if "%s.blender" % __name__ in sys.modules:
        import importlib

        def reload_mod(name):
            modname = "%s.%s" % (__name__, name)
            try:
                old_module = sys.modules[modname]
            except KeyError:
                # Wasn't loaded before -- can happen after an upgrade.
                new_module = importlib.import_module(modname)
            else:
                new_module = importlib.reload(old_module)

            sys.modules[modname] = new_module
            return new_module

        reload_mod("alioss")

        async_loop = reload_mod("async_loop")
        model = reload_mod("model")
        auth = reload_mod("auth")
        appdir = reload_mod("appdir")
        panels = reload_mod("panels")
        ai_model = reload_mod("ai_model")
        preferences = reload_mod("preferences")

    else:
        from . import (
            async_loop,
            model,
            auth,
            panels,
            ai_model,
            preferences,
        )

    async_loop.setup_asyncio_executor()
    async_loop.register()
    model.register()
    auth.register()
    panels.register()
    ai_model.register()
    preferences.register()





def _monkey_patch_requests():
    """Monkey-patch old versions of Requests.

    This is required for the Mac version of Blender 2.77a.
    """

    import requests

    if requests.__build__ >= 0x020601:
        return

    log.info("Monkey-patching requests version %s", requests.__version__)
    from requests.packages.urllib3.response import HTTPResponse

    HTTPResponse.chunked = False
    HTTPResponse.chunk_left = None


def unregister():
    from . import (
        async_loop,
        model,
        auth,
        panels,
        ai_model,
        preferences,
    )

    async_loop.unregister()
    model.unregister()
    auth.unregister()
    panels.unregister()
    ai_model.unregister()
    preferences.unregister()

    # import pip
    # pip.main(['uninstall', 'oss2'])
