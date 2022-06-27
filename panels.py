
import bpy

from . import addon_updater_ops
from . import model


class OPR_OT_copy_url(bpy.types.Operator):
    bl_idname = 'opr.copy_url'
    bl_label = 'copy shared url'
    bl_description = "复制分享链接"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.window_manager.clipboard = context.scene.url
        return {'FINISHED'}


class VIEW3D_PT_object_upload(bpy.types.Panel):
    # ...
    bl_label = 'G3D Model Upload'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "分享"

    PROPS = [
        ('filename', bpy.props.StringProperty(name='Filename', default='文件名称')),
        ('url', bpy.props.StringProperty(name='Url', default='')),
        ('status', bpy.props.StringProperty(name='Status', default="")),
        ('progress', bpy.props.IntProperty(name='Progress', default=0, soft_max=100, soft_min=0, subtype="PERCENTAGE")),
    ]

    def draw(self, context):
        col = self.layout.column()
        for (prop_name, _) in self.PROPS:
            row = col.row()
            if prop_name in ('status', 'progress'):
                row = row.row()
                row.enabled = False
            row.prop(context.scene, prop_name)
            if prop_name == 'url':
                row.operator(OPR_OT_copy_url.bl_idname, text="", icon='COPY_ID')

        col.operator(model.OPR_OT_upload_model.bl_idname, text='Upload')

CLASSES = [
    OPR_OT_copy_url,
    VIEW3D_PT_object_upload,
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
