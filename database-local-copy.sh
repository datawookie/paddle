#!/bin/bash

while true
do
    COPY_PATH=kanoe-$(date +%Y%m%d-%H%M%S).db
    echo "Copy: $COPY_PATH."
    cp kanoe.db $COPY_PATH
    sleep 300
done
