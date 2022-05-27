class STSGetFailedError(RuntimeError):
    """
    获取OSS STS失败
    """
    pass


class RecordCreateError(RuntimeError):
    """
    创建上传记录失败
    """
    pass


class UserNotLoginError(RuntimeError):
    """
    用户未登录
    """
    pass


class UnknownError(RuntimeError):
    """
    未知错误
    """
    pass