# -*- coding: utf-8 -*-
import argparse
import glob
from pydoc import cli
import uuid
import os
from typing import Dict, Tuple, List
import time
from concurrent.futures import ThreadPoolExecutor, Future

import wget
import oss2
from alibabacloud_alimt20181012.client import Client as alimt20181012Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alimt20181012 import models as alimt_20181012_models

TRANSLATE_ACCESS_KEY = os.getenv('TRANSLATE_ACCESS_KEY')
TRANSLATE_SECRET_KEY = os.getenv('TRANSLATE_SECRET_KEY')
TRANSLATE_BUCKET_ENDPOINT = os.getenv('TRANSLATE_BUCKET_ENDPOINT')
TRANSLATE_BUCKET_NAME = os.getenv('TRANSLATE_BUCKET_NAME')

N_RETRY_S: int = 120
N_PROCS: int = 8
OUTPUT_DIR: str = './'


def check_params():
    global TRANSLATE_ACCESS_KEY, TRANSLATE_SECRET_KEY, TRANSLATE_BUCKET_ENDPOINT, TRANSLATE_BUCKET_NAME

    if TRANSLATE_ACCESS_KEY is None:
        TRANSLATE_ACCESS_KEY = input('TRANSLATE_ACCESS_KEY:')
    if TRANSLATE_SECRET_KEY is None:
        TRANSLATE_SECRET_KEY = input('TRANSLATE_SECRET_KEY')
    if TRANSLATE_BUCKET_ENDPOINT is None:
        TRANSLATE_BUCKET_ENDPOINT = input('TRANSLATE_BUCKET_ENDPOINT')
    if TRANSLATE_BUCKET_NAME is None:
        TRANSLATE_BUCKET_NAME = input('TRANSLATE_BUCKET_NAME')


def put_file_to_oss(bucket: oss2.Bucket, file_path: str, timeout: int = 120) -> Tuple[str, str]:

    object_name = str(uuid.uuid1()) + '_' + os.path.splitext(file_path)[-1]
    with open(file_path, 'rb') as fileobj:
        fileobj.seek(0, os.SEEK_SET)
        bucket.put_object(object_name, fileobj)

    url = bucket.sign_url('GET', object_name, timeout, slash_safe=True)

    return object_name, url


def delete_object_from_oss(bucket: oss2.Bucket, object_name: str) -> bool:
    bucket.delete_object(object_name)
    return True


def create_translation_task_from_url(client, url: str, src_lang: str,
                                     dst_lang: str) -> alimt_20181012_models.CreateDocTranslateTaskResponse:
    # -*- coding: utf-8 -*-
    # This file is auto-generated, don't edit it. Thanks.

    create_doc_translate_task_request = alimt_20181012_models.CreateDocTranslateTaskRequest(source_language=src_lang,
                                                                                            target_language=dst_lang,
                                                                                            file_url=url)
    res = client.create_doc_translate_task(create_doc_translate_task_request)
    return res


def get_translation_task(client, task_id: str) -> alimt_20181012_models.GetDocTranslateTaskResponse:
    config = open_api_models.Config(access_key_id=TRANSLATE_ACCESS_KEY, access_key_secret=TRANSLATE_SECRET_KEY)
    config.endpoint = 'mt.aliyuncs.com'
    client = alimt20181012Client(config)

    get_doc_translate_task_request = alimt_20181012_models.GetDocTranslateTaskRequest(task_id=task_id)
    res = client.get_doc_translate_task(get_doc_translate_task_request)
    return res


def submit_translation_task(bucket, client, filename, src_lang, dst_lang):
    print(f"[ Info ] Putting file {filename} to OSS")
    object_name, url = put_file_to_oss(bucket, filename)
    res = create_translation_task_from_url(client, url, src_lang, dst_lang)
    if not res.body.status == 'ready':
        print(f"[ Error ] Failed to translate document Result: {res}")
    return {'object_name': object_name, 'res': res, 'filename': filename}


def download_translation_task(bucket, client, task_future: Future):
    task = task_future.result()
    task_id = task['res'].body.task_id
    filename_out = task['filename'] + '.docx'
    object_name = task['object_name']

    print(f"[ Info ] Successfully created translation task. ID : {task_id}")

    # Wait
    for _ in range(int(N_RETRY_S / 5)):
        res = get_translation_task(client, task_id)
        if (res.body.status == 'translated'):
            break
        time.sleep(5)
        print('.', end='')
    print('')

    # Download
    if (res.body.status == 'translated'):
        print(f"[ Info ] Successfully translated document. URL : {res.body.translate_file_url}")
        wget.download(res.body.translate_file_url, out=os.path.join(OUTPUT_DIR,filename_out))
    else:
        print(f"[ Error ] Failed to translate document Result: {res}")

    delete_object_from_oss(bucket, object_name)


def process_file_url(url, client, src_lang, dst_lang):
    res = create_translation_task_from_url(client, url, src_lang, dst_lang)

    if res.body.status == 'ready':
        task_id = res.body.task_id
        print(f"[ Info ] Successfully created translation task. ID : {task_id}")
        for _ in range(int(N_RETRY_S / 10)):
            res = get_translation_task(client, task_id)
            if (res.body.status == 'translated'):
                break
            time.sleep(10)
            print('.', end='')
        print()
        if (res.body.status == 'translated'):
            print(f"[ Info ] Successfully translated document. URL : {res.body.translate_file_url}")
            wget.download(res.body.translate_file_url)
        else:
            print(f"[ Error ] Failed to translate document Result: {res}")

    else:
        print(f"[ Error ] Failed to translate document Result: {res}")


def process_file(bucket, client, filename, src_lang, dst_lang):
    object_name, url = put_file_to_oss(bucket, filename)
    process_file_url(url, client, src_lang, dst_lang)
    delete_object_from_oss(bucket, object_name)


def process_file_api(url, access_key, secret_key, src_lang, dst_lang):
    config = open_api_models.Config(access_key_id=access_key, access_key_secret=secret_key)
    config.endpoint = 'mt.aliyuncs.com'
    client = alimt20181012Client(config)
    process_file_url(url, client, src_lang, dst_lang)


def main():
    global OUTPUT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", "-s", type=str, default="en")
    parser.add_argument("--dst", "-d", type=str, default="zh")
    parser.add_argument("--filename", "-f", type=str, default=None)
    parser.add_argument("--output_dir", "-o", type=str, default=None)
    args = parser.parse_args()

    FILENAME: str = args.filename
    if FILENAME is not None:
        if ',' in FILENAME:
            TARGETS = FILENAME.split(',')
        else:
            TARGETS = glob.glob(FILENAME)
    else:
        print('[ Error ] Empty file')
        exit(1)

    SRC_LANG: str = args.src
    DST_LANG: str = args.dst
    if args.output_dir is not None:
        if not os.path.exists(args.output_dir):
            try:
                os.makedirs(args.output_dir)
            except Exception as e:
                print("[ Error ] Directory does not exist and cannot be created", e)
        if os.path.exists(args.output_dir):
            OUTPUT_DIR = args.output_dir
        else:
            OUTPUT_DIR = './'
    else:
        OUTPUT_DIR = './'
    print(f"[ Info ] Translated files will be saved to {OUTPUT_DIR}")
    check_params()

    auth = oss2.Auth(TRANSLATE_ACCESS_KEY, TRANSLATE_SECRET_KEY)
    bucket = oss2.Bucket(auth, TRANSLATE_BUCKET_ENDPOINT, TRANSLATE_BUCKET_NAME)

    config = open_api_models.Config(access_key_id=TRANSLATE_ACCESS_KEY, access_key_secret=TRANSLATE_SECRET_KEY)
    config.endpoint = 'mt.aliyuncs.com'
    client = alimt20181012Client(config)

    # bucket, client is needed here
    with ThreadPoolExecutor(N_PROCS) as pool:
        translate_tasks = [
            pool.submit(submit_translation_task, bucket, client, filename, SRC_LANG, DST_LANG) for filename in TARGETS
        ]
        [pool.submit(download_translation_task, bucket, client, task_future) for task_future in translate_tasks]


if __name__ == '__main__':
    main()
