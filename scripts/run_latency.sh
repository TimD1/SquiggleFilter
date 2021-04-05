#!/bin/bash

batch_sizes="1 10 50 100 250 300 400 512"
models="fast hac"

for model in $models; do
    echo "Model: $model"
    for bs in $batch_sizes; do
        python3 latency.py \
            $bs \
            --model $model \
            --basecall
    done
done
