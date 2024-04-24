#!/bin/bash

while true
do
    COPY_PATH=paddle-$(date +%Y%m%d-%H%M%S).db
    echo "Copy: $COPY_PATH."
    cp paddle.db $COPY_PATH
    sleep 60
done
