# Usage

## Set environment variables

```bash

export ACCESS_KEY=ExampleAccessKey
export SECRET_KEY=ExampleSecretKey
export BUCKET_ENDPOINT=ExampleBucketEndpoint
export BUCKET_NAME=ExampleBucketName
```

or modify the `aliyun_credentials.py`

```python
ACCESS_KEY = "ExampleAccessKey"
SECRET_KEY = "ExampleSecretKey"
BUCKET_ENDPOINT = "ExampleBucketEndpoint"
BUCKET_NAME = "ExampleBucketName"
```

Bucket endpoint looks like `oss-cn-shanghai.aliyuncs.com`

Aliyun's OSS service will be used to temporarily store the file. So the access key must have OSS access as well as MachineTranslation access.

## Run Python script

Translation from English to Chinese:

```bash
python aliyun_translate.py -f './Client_Selection_for_Federated_Learning_with_Heterogeneous_Resources_in_Mobile_Edge.pdf' \
                           --src=en \
                           --dst=zh
```

## Execute Python Module

```bash
python -m aliyun_translate -f './Client_Selection_for_Federated_Learning_with_Heterogeneous_Resources_in_Mobile_Edge.pdf' \
                           --src=en \
                           --dst=zh \
                           --output_dir="./out/"
```

| Argument            | Usage                                                   |
| ------------------- | ------------------------------------------------------- |
| `-filename` `-f`    | Input filename, can be `file1.pdf,file2.pdf` or `*.pdf` |
| `--src` `-s`        | Source language                                         |
| `--dst` `-d`        | Destination language                                    |
| `--output_dir` `-o` | Output directory, will create if not exists             |
