from glob import glob
import h5py
import subprocess
from bisect import bisect_left

'''
1. Download data from:  https://public-docs.crg.es/covid/
2. Sort mapping file:   cat assigned.txt | cut -f1 -d$'\t' | sort > human.txt
'''

main_data_dir = "../data"
species = "human"
basetype = "RNA"
dataset = "0"

data_dir = f"{main_data_dir}/{species}/{basetype}/{dataset}/fast5"
outfile = f"{main_data_dir}/{species}/{basetype}/{dataset}/mapped_reads.fast5"
mapped_reads_fn = f"{main_data_dir}/{species}/{basetype}/{dataset}/{species}.txt"
mapped_reads = [x.strip() for x in open(mapped_reads_fn, "r").readlines()]

def BinarySearch(a, x): 
    i = bisect_left(a, x) 
    if i != len(a) and a[i] == x: 
        return i 
    else: 
        return -1

total_unmapped = 0
total_mapped = 0
for fast5_fn in glob(f"{data_dir}/*.fast5"):
    print(fast5_fn)

    input_fast5 = h5py.File(fast5_fn, "r")
    for read_id in input_fast5:
        mapped = ( BinarySearch(mapped_reads, read_id[5:]) >= 0 )
        if mapped:
            total_mapped += 1
            subprocess.run(["h5copy", "-v", 
                    "-i", f"{fast5_fn}", 
                    "-s", f"{read_id}",
                    "-o", f"{outfile}",
                    "-d", f"{read_id}"])
        else:
            total_unmapped += 1
print(f"{total_mapped} reads mapped, {total_unmapped} reads unmapped.")



