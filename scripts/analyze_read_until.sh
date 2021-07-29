#!/bin/bash

python3 analyze_read_until.py \
    --save_scores \
    --plot_results \
    --virus_species covid \
    --other_species human \
    --basetype rtDNA

python3 analyze_read_until.py \
    --save_scores \
    --plot_results \
    --virus_species lambda \
    --other_species human \
    --basetype DNA
