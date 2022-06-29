import os
import time

import aiohttp
import bpy
from . import addon_updater_ops
from . import async_loop
from . import settings
from . import utils

ai_categories = {
    ("01", "单图草稿生成", "Single Draft"),
    ("02", "单张线稿生成", "Single Line Draft"),
    ("03", "多张照片生成", "Multi Photo"),
    ("04", "多张手绘生成", "Multi Line Draft"),
}

categories = {
    ("02691155", "待上线", "Default"),
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

multi_categories = {
    ("locked", "待上线", "locked"),
    ("keyboard", "键盘", "Keyboard"),
    ("staple", "订书机", "Staple"),
    ("airplane", "飞机", "Airplane"),
    ("bench", "长凳", "Bench"),
    ("tri-stand", "三脚架", "tri-stand"),
    ("car", "小汽车", "Car"),
    ("kettle", "水壶", "Kettle"),
    ("display", "显示器", "Display"),
    ("lamp", "台灯", "Lamp"),
    ("speaker", "扬声器", "Speaker"),
    ("rifle", "来福枪", "Rifle"),
    ("sofa", "沙发", "Sofa"),
    ("table", "桌子", "Table"),
    ("phone", "手机", "Phone"),
    ("iphone", "iphone", "iPhone"),
    ("boat", "船只", "Boat"),
    ("chair", "椅子", "Chair"),
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

        utils.show_message_box("功能待上线", "Ai model message", "INFO")
        return {'CANCEL'}
        print("start ....")
        start_time = time.time()
        picture_path = context.scene.picture

        if not picture_path:
            utils.show_message_box("请先选择图片", "Ai model message", "INFO")
            self.report(
                {'ERROR'},
                "please upload a picture first"
            )
            return {'CANCELLED'}

        self.report(
            {'INFO'},
            "模型生成中..."
        )
        url = f"{settings.AI_MODEL_SERVER}{context.scene.category}"
        filepath = context.scene.picture
        files = {'file': open(filepath, 'rb')}
        # await asyncio.sleep(10)
        # TODO use aiohttp
        # res = requests.post(url, files=files)
        # context.scene.aimodel_single_progress = 25
        # utils.refresh_all_areas()
        res, status = await self.request(url, files)
        # context.scene.aimodel_single_progress = 50
        # utils.refresh_all_areas()
        if status != 200:
            self.report(
                {'ERROR'},
                "ai server error"
            )
            return {'CANCELLED'}
        else:
            self.report(
                {'INFO'},
                "模型生成成功，正在保存模型..."
            )
            # write response into an obj file
            user_data_dir = utils.get_user_data_dir()
            name, suffix = os.path.splitext(os.path.basename(picture_path))
            obj_path = os.path.join(user_data_dir, "%s.obj" % str(name))
            with open(obj_path, mode='w') as f:
                f.write(res)

            # old_objs = set(bpy.data.objects)
            # max_x = max([(ob.location.x + ob.scale.x) for ob in old_objs])
            print("obj_path:", obj_path)
            # context.scene.aimodel_single_progress = 75
            # utils.refresh_all_areas()
            self.report(
                {'INFO'},
                "生成成功，正在下载模型..."
            )
            # bpy.ops.import_scene.obj(filepath=obj_path)
            bpy.ops.import_mesh.ply(filepath=obj_path)
            # context.scene.aimodel_single_progress = 100
            # utils.refresh_all_areas()
            # bpy.ops.import_scene.obj(filepath="D:\\glacierProjects\\blender_demos\\objs\\tem.obj")
        # imported_objs = set(bpy.data.objects) - old_objs

        # x_step = 1
        # for ob in imported_objs:
        #     ob_x_scale = ob.scale.x
        #     max_x = max_x + x_step + ob_x_scale
        #     ob.location.x = max_x

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
        picture_path = context.scene.picture_dir
        if not picture_path:
            utils.show_message_box("请先选择图片文件夹", "Ai model message", "INFO")

            self.report(
                {'ERROR'},
                "please upload a picture first"
            )
            return {'CANCELLED'}
        # url = f"{settings.AI_MODEL_MULTI_SERVER}{context.scene.multi_p_category}"
        url = f"{settings.AI_MODEL_MULTI_SERVER}"
        img_dir = context.scene.picture_dir

        files = os.listdir(img_dir)
        imgs = [f for f in files if f.endswith(".jpg") or f.endswith(".png")]

        files = {}
        for i, img in enumerate(imgs):
            img_path = os.path.join(img_dir, img)
            img_name, img_suf = os.path.splitext(img)
            files["%s%s" % (i, img_suf)] = open(img_path, 'rb')
        print("Start request：",url)
        res, status = await self.request(url, files)
        if status != 200:
            self.report(
                {'ERROR'},
                "ai server error"
            )
            return {'CANCELLED'}
        else:
            # write response into an obj file
            user_data_dir = utils.get_user_data_dir()
            # name, suffix = os.path.splitext(os.path.basename(picture_path))
            # print("name:", name)
            obj_path = os.path.join(user_data_dir, "ai_model.ply")

            with open(obj_path, mode='w') as f:
                f.write(res)

            # old_objs = set(bpy.data.objects)
            # max_x = max([(ob.location.x + ob.scale.x) for ob in old_objs])
            # bpy.ops.import_scene.obj(filepath=obj_path)
            bpy.ops.import_mesh.ply(filepath=obj_path)

        # imported_objs = set(bpy.data.objects) - old_objs

        # x_step = 1
        # for ob in imported_objs:
        #     ob_x_scale = ob.scale.x
        #     max_x = max_x + x_step + ob_x_scale
        #     ob.location.x = max_x

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
    bl_category = 'AI建模'
    bl_label = 'AI 建模'

    PROPS = [
        ('picture', bpy.props.StringProperty(name="图片", subtype='FILE_PATH', description="upload a picture")),
        ('ai_category',
         bpy.props.EnumProperty(name='建模方式', description='支持的AI建模的方式', items=ai_categories, default='03')),
        ('category', bpy.props.EnumProperty(name='分类', description='单图建模支持的类型', items=categories, default='02691155')),
        # ('aimodel_single_progress',
        #  bpy.props.IntProperty(name='Progress', default=0, soft_max=100, soft_min=0, subtype="PERCENTAGE")),
    ]

    def draw(self, context):
        addon_updater_ops.check_for_update_background()

        col = self.layout.column()
        for (prop_name, _) in self.PROPS:
            row = col.row()

            if prop_name == 'category':
                row.enabled = False
            row.prop(context.scene, prop_name)

        col.operator(OPR_OT_ai_model_generate_single.bl_idname, text="生成")
        addon_updater_ops.update_settings_ui(self, context)
        # addon_updater_ops.update_notice_box_ui(self, context)


class VIEW3D_PT_aimodel_multi(bpy.types.Panel):
    """
    ai generate an object through a picture
    """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI建模'
    bl_label = 'AI 多张照片建模'

    PROPS = [
        ('picture_dir', bpy.props.StringProperty(name="文件夹", subtype='DIR_PATH', description="upload a picture")),
        ('ai_category',
         bpy.props.EnumProperty(name='建模方式', description='支持的AI建模的方式', items=ai_categories, default='03')),
        ('multi_p_category',
         bpy.props.EnumProperty(name='分类', description='多图建模支持的类型', items=multi_categories, default='chair')),
    ]

    def draw(self, context):
        addon_updater_ops.check_for_update_background()

        col = self.layout.column()
        for (prop_name, _) in self.PROPS:
            row = col.row()

            if prop_name in ('multi_p_category','ai_category'):
                row.enabled = False

            row.prop(context.scene, prop_name)
        col.operator(OPR_OT_ai_model_generate_multi.bl_idname, text="生成")
        addon_updater_ops.update_settings_ui(self, context)


CLASSES = [
    # OPR_OT_ai_model_generate_single,
    OPR_OT_ai_model_generate_multi,
    # VIEW3D_PT_aimodel_single,
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
