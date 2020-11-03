#!/bin/bash

# Converts multi-fast5 files with one read to actual multi-fast5 files

data_dir="/z/scratch1/hariss/covid/forward_fast5"
reads=1000
output_dir="covid/fast5/$reads"

mkdir -p $output_dir

for rd in $(ls $data_dir | head -n $reads); do

    read_id=$(h5ls $data_dir/$rd | cut -f 1 -d " ")

    h5copy \
        -v \
        -i "$data_dir/$rd" \
        -s $read_id \
        -o "$output_dir/fwd.fast5" \
        -d $read_id

done
