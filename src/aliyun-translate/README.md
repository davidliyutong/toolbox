# Usage

## Introduction

To use this script you have to create an aliyun account and enable Object Storage Service(OSS) and Machine Translate (MT) service.

It is also recommended that you create DEDICATED PAM account when using these services.

## Environment setup

First, create a pair of access / secret keys that have access to OSS and MT service. Aliyun's OSS service will be used to temporarily store the file.

Second, create a OSS bucket in the nearest endpoint.

Add these credentials to your path variable

```bash

export TRANSLATE_ACCESS_KEY=ExampleAccessKey
export TRANSLATE_SECRET_KEY=ExampleSecretKey
export TRANSLATE_BUCKET_ENDPOINT=ExampleBucketEndpoint
export TRANSLATE_BUCKET_NAME=ExampleBucketName
```

> Bucket endpoint looks like `oss-cn-shanghai.aliyuncs.com`

If these variables are not set, the translator will ask for them in a interactive prompt.

## Run Python script

You can run the script directly

Translation from English to Chinese:

```bash
python ./aliyun_translate/translate.py -f './Input.pdf' \
                           --src=en \
                           --dst=zh
```

## Execute Python Module

To install the package, run:

```bash
python setup.py install
```

Or you can use pip to install `.whl` releases:

```bash
pip install aliyun_translate-<version>-<arch>.whl
```

Then run:

```bash
python -m aliyun_translate -f './Input' \
                           --src=en \
                           --dst=zh \
                           --output_dir="./Out/"
```

## Arguments

| Argument            | Usage                                                   |
| ------------------- | ------------------------------------------------------- |
| `-filename` `-f`    | Input filename, can be `file1.pdf,file2.pdf` or `*.pdf` |
| `--src` `-s`        | Source language                                         |
| `--dst` `-d`        | Destination language                                    |
| `--output_dir` `-o` | Output directory, will create if not exists             |
