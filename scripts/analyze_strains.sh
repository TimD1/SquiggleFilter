#!/bin/bash

for seq in `seq 1 15`; do
    rm -rf ../results/covid_strains/strain${seq}_error_catalogue
    time assess_assembly \
        -t $(nproc) \
        -r ../data/covid_strains/0.fasta \
        -i ../data/covid_strains/$seq.fasta \
        -C \
        -p ../results/covid_strains/strain$seq
done
