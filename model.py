import hashlib
import os
from typing import List

import bpy

from . import alioss, log
from . import async_loop
from . import auth
from . import g3d
from . import routers
from . import status
from . import utils
from .errors import RecordCreateError, UserNotLoginError, UnknownError


async def set_record_status(record_status: int, model_id: id):
    """
    设置模型状态
    :param model_id:
    :param record_status:
    :return:
    """
    res = routers.set_record_status(record_status, model_id)
    if res.status_code == status.HTTP_401_UNAUTHORIZED:
        UserNotLoginError()
    elif res.status_code != status.HTTP_200_OK:
        log.error("Unknown Error")
        raise UnknownError()
    else:
        return res.json()["data"]


async def set_batch_record_status(record_status: int, model_ids: List[int]):
    """
    批量设置模型状态
    :param model_ids:
    :param record_status:
    :return:
    """
    res = routers.set_batch_record_status(record_status, model_ids)
    if res.status_code == status.HTTP_401_UNAUTHORIZED:
        UserNotLoginError()
    elif res.status_code != status.HTTP_200_OK:
        log.error("Unknown Error")
        raise UnknownError()
    else:
        return res.json()["data"]


class UploadModel(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    # 该操作类的唯一ID，供其他类进行调用
    bl_idname = 'objects.upload_model'
    # 在operator操作中显示的名字
    bl_label = "上传本地的模型到G3D云资源中"
    bl_description = "上传本地的模型到G3D云资源中"
    bl_options = {'REGISTER', 'UNDO'}

    async def create_record(self, context, file_path: str):
        """
        创建记录
        :return:
        """
        # 1.获取filepath
        # 获取file_name
        # file_name = os.path.basename(file_path)
        file_name = context.scene.filename
        # 2.生成md5
        f = open(file_path, 'rb')
        file_content = f.read()
        md5 = hashlib.md5(file_content).hexdigest()
        # 3.生成file_size
        file_meta = os.stat(file_path)
        total_size = file_meta.st_size
        # 4.创建记录
        data = {
            "filename": "%s.obj" % file_name,
            "md5": md5,
            "size": total_size,
        }

        res = routers.create_upload_record(data)
        if res.status_code != status.HTTP_201_CREATED:
            raise RecordCreateError(res.json())
        return res.json()["data"]

    def upload_model(self, context, oss_path, file_path):
        """
        上传文件
        :return:
        """
        data = auth.check_sts_token()
        access_key_id = data["AccessKeyId"]
        access_key_secret = data["AccessKeySecret"]
        security_token = data["SecurityToken"]
        ali_oss = alioss.AliObject(access_key_id, access_key_secret, security_token, context)

        ret = ali_oss.resumable_upload(oss_path, file_path)

    def export_model(self, ) -> str:
        """
        导出当前场景scene文件为obj
        :return:
        """
        user_data_dir = utils.get_user_data_dir()
        obj_path = os.path.join(user_data_dir, "temp.obj")

        bpy.ops.export_scene.obj(filepath=obj_path)

        return obj_path

    # 必须要实现的父类的接口
    async def async_execute(self, context):
        """Entry point of the asynchronous operator.
        Implement in a subclass.
        """
        # 导出模型
        context.scene.status = '正在上传'
        context.scene.url = ''
        context.scene.progress = 0

        file_path = await g3d.async_func_call(self.export_model)
        try:
            # 创建记录

            record_data = await self.create_record(context, file_path)
            oss_path = record_data["oss_path"]
            model_id = record_data["id"]
            # 上传
            await g3d.async_func_call(self.upload_model, context, oss_path, file_path)
            # 更新记录
            data = await set_record_status(routers.STATUS_COMPLETE, model_id)
            context.scene.url = data["share_url"]
            context.scene.status = '上传成功'
        except Exception as e:
            context.scene.status = '上传失败'
            log.error(str(e))

        return {'FINISHED'}


class GetModelUploadList(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.model_upload_list'
    bl_label = "获取这个用户已经上传的模型列表"
    bl_description = "获取这个用户已经上传的模型列表"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        获取这个用户已经上传的模型列表
        """
        params = {
            "page": 1,
            "page_size": 15,
        }
        res = routers.get_upload_list(params)
        if res != status.HTTP_200_OK:
            raise UnknownError()
        else:
            return res.json()["data"]


class RenameModel(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.rename_model'
    bl_label = "对模型重命名"
    bl_description = "对模型重命名"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        获取这个用户已经上传的模型列表
        """
        # TODO GET MODEL ID AND MODEL NAME
        model_id = 25
        name = "model"
        res = routers.rename_model(name, model_id)
        if res.status_code != status.HTTP_200_OK:
            raise UnknownError()
        return res.json()["data"]


class RecycleModel(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.recycle_model_batch'
    bl_label = "将模型放入回收站"
    bl_description = "逻辑删除模型"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        # TODO GET MODEL ID
        model_id = 25
        await set_record_status(routers.STATUS_DELETED, model_id)


class RecycleModelBatch(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.recycle_model_batch'
    bl_label = "将模型批量放入回收站"
    bl_description = "逻辑批量删除模型"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        批量放入回收站
        """
        # TODO GET MODEL IDS
        await set_batch_record_status(routers.STATUS_DELETED, [1, 2, 3])


class RecoveryModel(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.recovery_model'
    bl_label = "从回收站中还原模型"
    bl_description = "设置模型状态为正常"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        # TODO GET MODEL ID
        model_id = 25
        await set_record_status(routers.STATUS_DELETED, model_id)


class RecoveryModelBatch(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.recovery_model_batch'
    bl_label = "将模型批量从回收站还原"
    bl_description = "批量更改模型状态"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        批量放入回收站
        """
        # TODO GET MODEL IDS
        await set_batch_record_status(routers.STATUS_DELETED, [1, 2, 3])


class GetModelRecycledList(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.model_upload_list'
    bl_label = "获取回收站内的模型列表"
    bl_description = "获取回收站内的模型列表"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        获取回收站内的模型列表
        """
        params = {
            "page": 1,
            "page_size": 15,
            "ordering": "-created_at"
        }
        res = routers.get_recycle_list(params)
        if res.status_code != status.HTTP_200_OK:
            raise UnknownError()
        else:
            return res.json()["data"]


class DeleteModel(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.delete_model'
    bl_label = "删除回收站内的模型"
    bl_description = "删除回收站内的模型"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        删除指定模型
        """
        # TODO GET MODEL ID
        model_id = 25
        res = routers.delete_model(model_id)
        if res != status.HTTP_204_NO_CONTENT:
            raise UnknownError()
        else:
            return "delete successfully"


class DeleteBatchModel(async_loop.AsyncModalOperatorMixin, bpy.types.Operator):
    bl_idname = 'objects.delete_model'
    bl_label = "批量删除回收站内的模型"
    bl_description = "批量删除回收站内的模型"
    bl_options = {'REGISTER', 'UNDO'}

    async def async_execute(self, context):
        """
        获取这个用户已经上传的模型列表
        """
        # TODO GET MODEL IDS
        await set_batch_record_status(routers.STATUS_DESTROY, [1, 2, 3])


def register():
    bpy.utils.register_class(UploadModel)


def unregister():
    bpy.utils.unregister_class(UploadModel)
