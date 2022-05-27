from typing import List

import requests
from requests import Response

from .settings import TEMPORARY_TOKEN, G3D_SERVER_URL

headers = {"token": TEMPORARY_TOKEN}

STATUS_UPLOADING = 1
STATUS_COMPLETE = 2
STATUS_DELETED = 0
STATUS_DESTROY = -1


def concat_url(url_path: str, domain: str = G3D_SERVER_URL, ) -> str:
    return domain + url_path


def get_sts_token() -> Response:
    """
    上传前创建记录
    :return:
    """
    url = concat_url("/api/v1/gmodel/sts_credentials/")
    res = requests.get(url, headers=headers)
    return res


def create_upload_record(body: dict, ) -> Response:
    """
    上传前创建记录
    :return:
    """
    url = concat_url("/api/v1/gmodel/")
    res = requests.post(url, body, headers=headers)
    return res


def set_record_status(status: int, model_id: int) -> Response:
    """
    更新模型记录
    :return:
    """
    url = concat_url("/api/v1/gmodel/{id}/".format(id=model_id))
    data = {
        "status": status
    }
    res = requests.put(url, data, headers=headers)
    return res


def set_batch_record_status(status: int, ids: List[int]) -> Response:
    """
    批量更新模型记录
    :return:
    """
    url = concat_url("/api/v1/gmodel/batch/")
    data = {
        "ids": ids,
        "status": status
    }
    res = requests.put(url, data, headers=headers)
    return res


def get_upload_list(page_params: dict) -> Response:
    """
    获取已上传的记录
    :return:
    """
    url = concat_url("/api/v1/gmodel/")
    res = requests.get(url, params=page_params, headers=headers)
    return res


def rename_model(name: str, model_id: int) -> Response:
    """
    模型重命名
    :return:
    """
    url = concat_url("/api/v1/gmodel/{id}/".format(id=model_id))
    data = {
        "filename": name
    }
    res = requests.put(url, data, headers=headers)
    return res


def get_recycle_list(page_params: dict) -> Response:
    """
    获取回收站内的记录
    :return:
    """
    url = concat_url("/api/v1/gmodel/recycle/")
    res = requests.get(url, params=page_params, headers=headers)
    return res


def delete_model(model_id: int) -> Response:
    """
    删除模型
    :return:
    """
    url = concat_url("/api/v1/gmodel/{id}/".format(id=model_id))
    res = requests.delete(url, headers=headers)
    return res
