#!/bin/bash

basetype="$1";
model="fast"

if [ "$basetype" == "dna" ]; then
    config="dna_r9.4.1_450bps_$model.cfg"
    port=1234
elif [ "$basetype" == "rna" ]; then
    config="rna_r9.4.1_70bps_$model.cfg"
    port=2345
elif [ "$basetype" == "" ]; then
    # just do DNA
    config="dna_r9.4.1_450bps_$model.cfg"
    port=1234
else
    echo "Invalid base type, must be 'rna' or 'dna'"
    exit 1
fi

guppy_basecall_server \
    --config $config \
    --trim_strategy none \
    --port $port \
    --log_path /tmp/guppy_log \
    --device cuda:0

