import os
import re

import oss2
from loguru import logger

from utils.config_manager import config_manager
from utils.image_processors import BaseImageUploader


class AliOSSHandler(BaseImageUploader):
    BASIC_URL = ''

    def __init__(self):
        super().__init__()
        ak = config_manager.config.pic_config.ali_oss["ali_oss_ak"]
        sk = config_manager.config.pic_config.ali_oss["ali_oss_sk"]
        bucket_url = config_manager.config.pic_config.ali_oss['ali_bucket']
        if ak and sk and bucket_url:
            self.BASIC_URL = bucket_url
            bucket_name, endpoint = self._split_url()
            auth = oss2.Auth(ak, sk)
            self.bucket = oss2.Bucket(auth, f'{endpoint}', bucket_name)
            self.get_storage_desc()
        else:
            logger.warning('failed to start ali oss service')
            self.bucket = None

    def _split_url(self):
        re_ = re.search(r'https://(.*?)\.(oss-.*?\.aliyuncs.com)/?', self.BASIC_URL)
        if re_:
            bucket_name, endpoint = re_.groups()
        else:
            raise Exception('failed to split bucket url.')
        return bucket_name, endpoint

    def get_storage_desc(self):
        bucket_stat = self.bucket.get_bucket_stat()
        print('storage: ' + str(bucket_stat.storage_size_in_bytes))
        print('object count: ' + str(bucket_stat.object_count))
        print('multi part upload count: ' + str(bucket_stat.multi_part_upload_count))

    def validate_pic(self, name) -> bool:
        return self.bucket.object_exists(name)

    def upload_pic(self, path, filename):
        if self.validate_pic(filename):
            logger.info('{} already exists'.format(filename))
            return self.BASIC_URL + filename

        logger.info('uploading {}'.format(filename))
        with open(path, 'rb') as fileobj:
            fileobj.seek(0, os.SEEK_SET)
            # current = fileobj.tell()
            try:
                self.bucket.put_object(filename, fileobj)
                logger.info('uploaded {}'.format(filename))
            except Exception as _e:
                logger.warning('failed to upload {}, exception: {}'.format(filename, _e))

        return self.BASIC_URL + filename


oss_handler = AliOSSHandler()
