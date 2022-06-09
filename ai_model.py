import os
import time

import aiohttp
import bpy

from . import async_loop
from . import utils

categories = {
    ("02691156", "飞机", "Airplane"),
    ("02828884", "长凳", "Bench"),
    ("02933112", "内阁", "Cabinet"),
    ("02958343", "小汽车", "Car"),
    ("03001627", "椅子", "Chair"),
    ("03211117", "显示器", "Display"),
    ("03636649", "台灯", "Lamp"),
    ("03691459", "扬声器", "Loudspeaker"),
    ("04090263", "来福枪", "Rifle"),
    ("04256520", "沙发", "Sofa"),
    ("04379243", "桌子", "Table"),
    ("04401088", "电话", "Telephone"),
    ("04530566", "船只", "Watercraft"),
}


class OPR_OT_ai_model_generate_single(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    """
    upload a picture to ai server and get a object from response
    """
    bl_idname = 'opr.ai_model_generate_single'
    bl_label = 'generate a object through a picture'
    bl_description = "通过单张图片AI生成模型"
    bl_options = {'REGISTER', 'UNDO'}

    # picture: bpy.props.StringProperty(
    #     name="Upload",
    #     subtype='FILE_PATH',
    #     description="upload a picture"
    # )

    async def request(self, url, files):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=files) as response:
                return await response.text(), response.status

    async def async_execute(self, context):
        self.report(
            {'INFO'},
            "模型生成中..."
        )
        start_time = time.time()
        picture_path = context.scene.picture
        if not picture_path:
            utils.show_message_box("请先选择图片", "Ai model message", "INFO")

            self.report(
                {'ERROR'},
                "please upload a picture first"
            )
            return {'CANCELLED'}
        url = f"http://192.168.1.26:80/api/generate/sketch/{context.scene.category}"
        print("url:", url)
        print("picture_path", picture_path)
        filepath = context.scene.picture
        files = {'file': open(filepath, 'rb')}
        # await asyncio.sleep(10)
        print("Requesting")
        # TODO use aiohttp
        # res = requests.post(url, files=files)
        res, status = await self.request(url, files)
        print("Requesting over", status)
        print(res)
        if status != 200:
            self.report(
                {'ERROR'},
                "ai server error"
            )
            # return {'CANCELLED'}
        else:
            # write response into an obj file
            user_data_dir = utils.get_user_data_dir()
            name, suffix = os.path.splitext(os.path.basename(picture_path))
            print("name", name)
            obj_path = os.path.join(user_data_dir, "%.obj" % str(name))

            with open(obj_path, mode='w') as f:
                f.write(res)

        old_objs = set(bpy.data.objects)
        max_x = max([(ob.location.x + ob.scale.x) for ob in old_objs])
        bpy.ops.import_scene.obj(filepath="D:\\glacierProjects\\blender_demos\\objs\\tem.obj")
        imported_objs = set(bpy.data.objects) - old_objs

        x_step = 1
        for ob in imported_objs:
            ob_x_scale = ob.scale.x
            max_x = max_x + x_step + ob_x_scale
            ob.location.x = max_x

        end_time = time.time()
        utils.show_message_box("模型生成成功", "Ai model message", "INFO")
        print("spend time:", (end_time - start_time))
        return {'FINISHED'}


class OPR_OT_ai_model_generate_multi(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    """
    upload a picture to ai server and get a object from response
    """
    bl_idname = 'opr.ai_model_generate_multi'
    bl_label = 'generate a object through a picture'
    bl_description = "通过单张图片AI生成模型"
    bl_options = {'REGISTER', 'UNDO'}

    # picture: bpy.props.StringProperty(
    #     name="Upload",
    #     subtype='FILE_PATH',
    #     description="upload a picture"
    # )

    async def request(self, url, files):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=files) as response:
                return await response.text(), response.status

    async def async_execute(self, context):
        self.report(
            {'INFO'},
            "模型生成中..."
        )
        start_time = time.time()
        picture_path = context.scene.picture
        if not picture_path:
            utils.show_message_box("请先选择图片文件夹", "Ai model message", "INFO")

            self.report(
                {'ERROR'},
                "please upload a picture first"
            )
            return {'CANCELLED'}
        url = f"http://192.168.1.26:80/api/generate/sketch/{context.scene.category}"
        print("url:", url)
        print("picture_path", picture_path)
        filepath = context.scene.picture
        files = {'file': open(filepath, 'rb')}
        # await asyncio.sleep(10)
        print("Requesting")
        # TODO use aiohttp
        # res = requests.post(url, files=files)
        res, status = await self.request(url, files)
        print("Requesting over", status)
        print(res)
        if status != 200:
            self.report(
                {'ERROR'},
                "ai server error"
            )
            # return {'CANCELLED'}
        else:
            # write response into an obj file
            user_data_dir = utils.get_user_data_dir()
            name, suffix = os.path.splitext(os.path.basename(picture_path))
            print("name", name)
            obj_path = os.path.join(user_data_dir, "%.obj" % str(name))

            with open(obj_path, mode='w') as f:
                f.write(res)

        old_objs = set(bpy.data.objects)
        max_x = max([(ob.location.x + ob.scale.x) for ob in old_objs])
        bpy.ops.import_scene.obj(filepath="D:\\glacierProjects\\blender_demos\\objs\\tem.obj")
        imported_objs = set(bpy.data.objects) - old_objs

        x_step = 1
        for ob in imported_objs:
            ob_x_scale = ob.scale.x
            max_x = max_x + x_step + ob_x_scale
            ob.location.x = max_x

        end_time = time.time()
        utils.show_message_box("模型生成成功", "Ai model message", "INFO")
        print("spend time:", (end_time - start_time))
        return {'FINISHED'}


class VIEW3D_PT_aimodel_single(bpy.types.Panel):
    """
    ai generate an object through a picture
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '分享'
    bl_label = 'AI 单图建模'

    PROPS = [
        ('picture', bpy.props.StringProperty(name="上传", subtype='FILE_PATH', description="upload a picture")),
        ('category', bpy.props.EnumProperty(name='分类', description='单图建模支持的类型', items=categories, default='02691156')),
    ]

    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in self.PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
        col.operator(OPR_OT_ai_model_generate_single.bl_idname, text="生成")


class VIEW3D_PT_aimodel_multi(bpy.types.Panel):
    """
    ai generate an object through a picture
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '分享'
    bl_label = 'AI 多图建模'

    PROPS = [
        ('picture_dir', bpy.props.StringProperty(name="文件夹", subtype='FILE_PATH', description="upload a picture")),
    ]

    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in self.PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
        col.operator(OPR_OT_ai_model_generate_multi.bl_idname, text="生成")


CLASSES = [
    OPR_OT_ai_model_generate_single,
    OPR_OT_ai_model_generate_multi,
    VIEW3D_PT_aimodel_single,
    VIEW3D_PT_aimodel_multi,
]


def register():
    for klass in CLASSES:
        if getattr(klass, "PROPS", None):
            for (prop_name, prop_value) in klass.PROPS:
                setattr(bpy.types.Scene, prop_name, prop_value)
        bpy.utils.register_class(klass)


def unregister():
    for klass in CLASSES:
        if getattr(klass, "PROPS", None):
            for (prop_name, prop_value) in klass.PROPS:
                delattr(bpy.types.Scene, prop_name)
        bpy.utils.unregister_class(klass)
