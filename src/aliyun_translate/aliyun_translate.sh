#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

export ACCESS_KEY="<ACCESS_KEY>"
export SECRET_KEY="<SECRET_KEY>"
export BUCKET_ENDPOINT="<ENDPOINT>"
export BUCKET_NAME="<BUCKETNAME>"

echo "Arguments: $*"
python $DIR/aliyun_translate.py $*