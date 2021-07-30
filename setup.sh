#!/bin/bash

echo -en "installing aws s3 (for downloading datasets)"
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
    -o "aws_cli_v2.zip" && \
    unzip aws_cli_v2.zip && \
    ./aws/install && \
    rm aws_cli_v2.zip && \
    rm -r ./aws
echo -e "done!"

echo -en "downloading covid data..."
mkdir -p data/covid/fast5 && \
    cd data/covid/fast5 && \
    wget https://cadde.s3.climb.ac.uk/SP1-raw.tgz && \
    tar -xvf SP1-raw.tgz && \
    rm SP1-raw.tgz && \
    cd -
echo -e "done!"

echo -en "downloading human data..."
mkdir -p data/human/fast5 && \
    aws s3 --no-sign-request sync \
        s3://ont-open-data/gm24385_2020.09/analysis/r9.4.1/20200914_1357_1-E11-H11_PAF272_d3c9678e/guppy_v4.0.11_r9.4.1_hac_prom/align_unfiltered/chr19/fast5/ \
        data/human/fast5  
echo -e "done!"

echo -en "setting up virtual environment..."
python3.6 -m venv sf-venv3
source sf-venv3/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
ipython kernel install --name "sf-venv3" --user
echo -e "done!"
