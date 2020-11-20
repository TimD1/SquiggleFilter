#!/bin/bash

basetype="$1";

if [ "$basetype" == "dna" ]; then
    config="dna_r9.4.1_450bps_hac.cfg"
    port=1234
elif [ "$basetype" == "rna" ]; then
    config="rna_r9.4.1_70bps_hac.cfg"
    port=2345
else
    echo "Invalid base type, must be 'rna' or 'dna'"
    exit 1
fi

guppy_basecall_server \
    --config $config \
    --port $port \
    --log_path /tmp/guppy_log \
    --device cuda:0

