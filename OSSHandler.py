import os

import oss2
from loguru import logger


class OSSHandler:
    def __init__(self):
        ak = os.environ.get('ALI_OSS_AK')
        sk = os.environ.get('ALI_OSS_SK')
        auth = oss2.Auth(ak, sk)
        self.bucket = oss2.Bucket(auth, 'https://oss-cn-shanghai.aliyuncs.com', 'notion-oss-bucket')
        self.get_storage_desc()

    def get_storage_desc(self):
        bucket_stat = self.bucket.get_bucket_stat()
        print('storage: ' + str(bucket_stat.storage_size_in_bytes))
        print('object count: ' + str(bucket_stat.object_count))
        print('multi part upload count: ' + str(bucket_stat.multi_part_upload_count))

    def validate_pic(self, name) -> bool:
        return self.bucket.object_exists(name)

    def upload_pic(self, path, filename):
        basic_url = 'https://notion-oss-bucket.oss-cn-shanghai.aliyuncs.com/'
        if self.validate_pic(filename):
            logger.info('{} already exists'.format(filename))
            return basic_url + filename

        logger.info('uploading {}'.format(filename))
        with open(path, 'rb') as fileobj:
            fileobj.seek(0, os.SEEK_SET)
            # current = fileobj.tell()
            self.bucket.put_object(filename, fileobj)
        logger.info('uploaded {}'.format(filename))

        return basic_url + filename


oss_handler = OSSHandler()
