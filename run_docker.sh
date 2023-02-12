#!/bin/bash

docker run -it \
    --rm \
    --mount type=bind,source=$(pwd)/src/images,target=/src/images \
    --name=bdsmlr bdsmlr:latest "$@"
