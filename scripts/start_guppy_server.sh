#!/bin/bash

guppy_basecall_server \
    --config dna_r9.4.1_450bps_hac.cfg \
    --port 1234 \
    --log_path /tmp/guppy_log \
    --device cuda:0
