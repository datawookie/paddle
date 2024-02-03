#!/bin/bash

# Will need to set up AWS CLI first, adding a set of default credentials.

while true
do
        aws s3 cp paddle.db s3://paddle-data/paddle-$(date +%Y%m%d-%H%M%S).db
        sleep 300
done
