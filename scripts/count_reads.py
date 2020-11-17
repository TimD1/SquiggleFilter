import glob
import h5py

main_dir = "/x/squiggalign_data"

for virus, basetype, other in zip(
        ["covid", "covid", "lambda"], 
        ["RNA", "rtDNA", "DNA"],
        ["human", "human", "human"]):

    virus_dir = f"{main_dir}/{virus}/{basetype}/fast5"
    other_dir = f"{main_dir}/{other}/{basetype}/fast5"

    virus_reads = 0
    for virus_fast5_fn in glob.glob(f"{virus_dir}/*.fast5"):
        virus_fast5 = h5py.File(virus_fast5_fn, 'r')
        for read in virus_fast5:
            virus_reads += 1
            if not virus_reads % 10000:
                print(f"...{virus_reads}\t{virus} {basetype} reads")

    other_reads = 0
    for other_fast5_fn in glob.glob(f"{other_dir}/*.fast5"):
        other_fast5 = h5py.File(other_fast5_fn, 'r')
        for read in other_fast5:
            other_reads += 1
            if not other_reads % 10000:
                print(f"...{other_reads}\t{other} {basetype} reads")
        
    print(f"\n{virus_reads}\t{virus} {basetype} reads")
    print(f"{other_reads}\t{other} {basetype} reads")
