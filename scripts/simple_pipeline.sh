#!/bin/bash

# set datasets
virus="lambda/DNA/0"
other="human/DNA/0"

# set project filepaths
proj_dir="../data"

# pipeline options
do_read_until=true
do_assembly=true
do_consensus=true
run_medaka=true

# set software filepaths
main_dir="/home/timdunn"
minimap_dir="$main_dir/software/minimap2"
racon_dir="$main_dir/software/racon/build/bin"
medaka_train_dir="$main_dir/software/medaka/venv/bin"
samtools_dir="$main_dir/software/samtools-1.10"
source ~/miniconda3/etc/profile.d/conda.sh

# set colors
G1='\033[0;32m'
G2='\033[0m'
R1='\033[0;31m'
R2='\033[0m'
Y1='\033[0;33m'
Y2='\033[0m'
export PS1=${PS1:-}

echo -e "\n${Y1}###############################${Y2}"
echo -e "${Y1}########## $virus ##########${Y2}"
echo -e "${Y1}##############################${Y2}\n"

if $do_read_until; then
    echo -e "${G1}Running Read-Until${G2}"
    source ../venv3/bin/activate
    python3 read_until.py \
        --virus_dir $proj_dir/$virus \
        --other_dir $proj_dir/$other \
        --basetype dna \
        --model_type fast \
        --basecall \
        --ratio 100 \
        --max_reads 440000 \
        --target_coverage 30 \
        --batch_size 5 \
        --chunk_lengths 2000
    deactivate
else
    echo -e "${R1}[Skipping Read-Until]${R2}\n"
fi

if $do_assembly; then
    mkdir -p $proj_dir/$virus/draft_assemblies
    echo -e "${G1}Running MiniMap2...${G2}"
    time $minimap_dir/minimap2 \
        -ax map-ont \
        --eqx \
        --cap-sw-mem=4g \
        -k 20 \
        -t $(nproc) \
        $proj_dir/$virus/reference.fasta \
        $proj_dir/$virus/fastq/all.fastq \
        > $proj_dir/$virus/aligned/calls_to_ref.sam
    echo -e "${G1}done\n${G2}"
else
    echo -e "${R1}[Skipping Assembly]${R2}\n"
fi

if $do_consensus; then
    echo -e "${Y1}[Selected RaCon Consensus]${Y2}\n"
    rm -rf $proj_dir/$virus/racon_consensus
    mkdir -p $proj_dir/$virus/racon_consensus
    echo -e "${G1}Calling RaCon consensus...${G2}"
    time $racon_dir/racon \
        -t $(nproc) \
        -m 8 -x -6 -g -8 -w 500 \
        --quality-threshold 1.0 \
        $proj_dir/$virus/fastq/all.fastq \
        $proj_dir/$virus/aligned/calls_to_ref.sam \
        $proj_dir/$virus/reference.fasta \
        > $proj_dir/$virus/racon_consensus/consensus.fasta
    echo -e "${G1}done\n${G2}"
else
    echo -e "${R1}[Skipping RaCon Consensus]${R2}\n"
fi

if $run_medaka; then
    echo -e "${G1}Running Medaka...${G2}"
    rm -rf $proj_dir/$virus/medaka_consensus
    source ~/software/medaka/venv/bin/activate
    time medaka_consensus \
        -m r941_min_high_g360 \
        -t $(nproc) \
        -b 20 \
        -i $proj_dir/$virus/fastq/all.fastq \
        -d $proj_dir/$virus/racon_consensus/consensus.fasta \
        -o $proj_dir/$virus/medaka_consensus
    deactivate
    echo -e "${G1}done\n${G2}"
else
    echo -e "${R1}[Skipping Medaka Polishing]${R2}\n"
fi
