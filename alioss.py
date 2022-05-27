import os
import sys

import oss2


class AliObject():
    def __init__(self, access_key_id, access_key_secret, security_token, context):
        # 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
        self._auth = oss2.StsAuth(access_key_id=access_key_id, access_key_secret=access_key_secret,
                                  security_token=security_token)
        # yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
        # 填写Bucket名称，例如examplebucket。
        self.bucket = oss2.Bucket(self._auth, "https://oss-cn-beijing.aliyuncs.com", "glacier-oss")
        self.context = context

    def upload(self, file_name, data):
        result = self.bucket.put_object(file_name, data)
        return file_name

    def download(self, file_path, out_dir):
        filename = os.path.basename(file_path)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_path = os.path.join(out_dir, filename)
        result = self.bucket.get_object_to_file(file_path, out_path)
        return out_path

    def resumable_upload(self, oss_path, file_path):
        def percentage(consumed_bytes, total_bytes):
            if total_bytes:
                rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
                print('\r{0}% '.format(rate), end='')
                sys.stdout.flush()
                self.context.scene.progress = rate

        # 如果使用store指定了目录，则断点信息将保存在指定目录中。如果使用num_threads设置并发上传线程数，请将oss2.defaults.connection_pool_size设置为大于或等于并发上传线程数。默认并发上传线程数为1。
        result = oss2.resumable_upload(self.bucket, oss_path, file_path,
                                       # store=oss2.ResumableStore(root='/tmp'),
                                       # 指定当文件长度大于或等于可选参数multipart_threshold（默认值为10 MB）时，则使用分片上传。
                                       multipart_threshold=100 * 1024,
                                       # 设置分片大小，单位为字节，取值范围为100 KB~5 GB。默认值为100 KB。
                                       part_size=100 * 1024,
                                       # 设置上传回调进度函数。
                                       progress_callback=percentage,
                                       # 如果使用num_threads设置并发上传线程数，请将oss2.defaults.connection_pool_size设置为大于或等于并发上传线程数。默认并发上传线程数为1。
                                       num_threads=4)
        return result
