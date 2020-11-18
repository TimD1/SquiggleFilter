This folder contains all raw data (placed in sub-folders)

# File structure overview

```
<species>/
    <basetype>/
        <study\_id>/
            fast5/
                *.fast5
            */
            reference.fasta
```

# Data Overview

================================================================================
## covid
--------------------------------------------------------------------------------
### RNA
#### 0: 51,800 reads, mapped subset of unsorted reads from VeroInfected to COVID
From Vero Cell Paper, contains 879,679 reads total
https://www.biorxiv.org/content/10.1101/2020.03.12.988865v2.full.pdf
https://osf.io/8f6n9/
FAST5 data isn't sorted, but "assigned" file has mapped read IDs
https://public-docs.crg.es/covid/8F6N9\_Korea\_VeroInfected.Wuhan\_Hu\_1/
https://public-docs.crg.es/covid/8F6N9\_Korea\_VeroInfected.Wuhan\_Hu\_1.Spliced/
https://public-docs.crg.es/covid/8F6N9\_Korea\_VeroInfected.hg38/

--------------------------------------------------------------------------------
### rtDNA
#### 0: 1,382,016 reads, ARTIC tiled PCR, only COVID mapped
https://cadde.s3.climb.ac.uk/SP1-raw.tgz
https://virological.org/t/first-cases-of-coronavirus-disease-covid-19-in-brazil-south-america-2-genomes-3rd-march-2020/409



================================================================================
## lambda
--------------------------------------------------------------------------------
### DNA
#### 0: 21750 reads, single-run isolate
/mnt/Wadden\_backup/Archive/data/from\_gui/2/20190828\_1459\_MN28422\_FAL11227\_02f954b8
Jack's first run: lambdaphage isolate



================================================================================
## human
--------------------------------------------------------------------------------
### RNA
#### 0: 13,215 human mapped subset of mRNA from Vero Cell paper
From Vero Cell Paper, contains 879,679 reads total
https://www.biorxiv.org/content/10.1101/2020.03.12.988865v2.full.pdf
https://public-docs.crg.es/covid/8F6N9\_Korea\_VeroInfected.hg38/
#### 1: Control mRNA from Vero Cell paper, subset
https://public-docs.crg.es/covid/8F6N9\_Korea\_VeroControl.hg38/NanoPreprocess/fast5\_files/FAN04793\_bebd05e2\_0.fast5

https://github.com/nanopore-wgs-consortium/NA12878/blob/master/RNA.md
This link contains data from 27 runs
#### x: UCSC\_Run1\_20170907\_DirectRNA
#### y: OICR\_Run1\_20171006\_DirectRNA

--------------------------------------------------------------------------------
### rtDNA
#### 0: 1,688,470 reads, one Birmingham run
https://github.com/nanopore-wgs-consortium/NA12878/blob/master/RNA.md
Did have to filter out some 1D2 data from Github link

--------------------------------------------------------------------------------
### DNA
https://github.com/nanopore-wgs-consortium/NA12878/blob/master/Genome.md
This link contains data from 53 runs
#### 0: 442132 reads from Birmingham
http://s3.amazonaws.com/nanopore-human-wgs/rel6/MultiFast5Tars/FAB39043-3709921973\_Multi\_Fast5.tar
#### 1: 83299 reads from Notts
http://s3.amazonaws.com/nanopore-human-wgs/rel6/MultiFast5Tars/FAF15665-16056159\_Multi\_Fast5.tar
