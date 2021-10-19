# -*- coding: utf-8 -*-
import argparse
import uuid
import os
from typing import Tuple, List
import time
import wget

import oss2
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models

from aliyun_credentials import ACCESS_KEY, SECRET_KEY, BUCKET_ENDPOINT, BUCKET_NAME


def put_file_to_oss(bucket: oss2.Bucket, file_path: str, timeout: int = 120) -> Tuple[str, str]:

    object_name = str(uuid.uuid1()) + os.path.splitext(file_path)[-1]
    with open(file_path, 'rb') as fileobj:
        fileobj.seek(0, os.SEEK_SET)
        bucket.put_object(object_name, fileobj)

    url = bucket.sign_url('GET', object_name, timeout, slash_safe=True)

    return object_name, url


def delete_object_from_oss(bucket: oss2.Bucket, object_name: str) -> bool:
    bucket.delete_object(object_name)
    return True


def create_translation_task_from_url(client, url: str, src_lang: str, dst_lang: str) -> alimt_20181012_models.CreateDocTranslateTaskResponse:
    # -*- coding: utf-8 -*-
    # This file is auto-generated, don't edit it. Thanks.

    create_doc_translate_task_request = alimt_20181012_models.CreateDocTranslateTaskRequest(source_language=src_lang,
                                                                                            target_language=dst_lang,
                                                                                            file_url=url)
    res = client.create_doc_translate_task(create_doc_translate_task_request)
    return res


def get_translation_task(client, task_id: str) -> alimt_20181012_models.GetDocTranslateTaskResponse:
    config = open_api_models.Config(access_key_id=ACCESS_KEY, access_key_secret=SECRET_KEY)
    config.endpoint = 'mt.aliyuncs.com'
    client = alimt20181012Client(config)

    get_doc_translate_task_request = alimt_20181012_models.GetDocTranslateTaskRequest(task_id=task_id)
    res = client.get_doc_translate_task(get_doc_translate_task_request)
    return res

def main(args):
    N_RETRY = 12

    FILENAME = args.filename
    SRC_LANG = args.src_lang
    DST_LANG = args.dst_lang
    auth = oss2.Auth(ACCESS_KEY, SECRET_KEY)
    bucket = oss2.Bucket(auth, BUCKET_ENDPOINT, BUCKET_NAME)

    config = open_api_models.Config(access_key_id=ACCESS_KEY, access_key_secret=SECRET_KEY)
    config.endpoint = 'mt.aliyuncs.com'
    client = alimt20181012Client(config)

    # bucket, client is needed here


    object_name, url = put_file_to_oss(bucket, FILENAME)
    res = create_translation_task_from_url(client, url, SRC_LANG, DST_LANG)

    if res.body.status == 'ready':
        task_id = res.body.task_id
        print(f"[ Info ] Successfully created translation task. ID : {task_id}")
        for i in range(N_RETRY):
            res = get_translation_task(client, task_id)
            if (res.body.status == 'translated'):
                break
            time.sleep(10)
            print('.', end='')
        print('')
        if (res.body.status == 'translated'):
            print(f"[ Info ] Successfully translated document. URL : {res.body.translate_file_url}")
            wget.download(res.body.translate_file_url)
        else:
            print(f"[ Error ] Failed to translate document Result: {res}")
            
    else:
        print(f"[ Error ] Failed to translate document Result: {res}")

    delete_object_from_oss(bucket, object_name)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_lang", type=str, default="en")
    parser.add_argument("--dst_lang", type=str, default="zh")
    parser.add_argument("--filename", "-f", type=str)
    args = parser.parse_args()
    main(args)
