#!/bin/bash

# Merges multi-fast5 files

data_dir="../data/human/fast5"
reads=1000
output_dir="../data/human/"

mkdir -p $output_dir

for rd in $(ls $data_dir | head -n $reads); do

    read_id=$(h5ls $data_dir/$rd | cut -f 1 -d " ")

    h5copy \
        -v \
        -i "$data_dir/$rd" \
        -s $read_id \
        -o "$output_dir/reads.fast5" \
        -d $read_id

done
