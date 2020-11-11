from glob import glob
import argparse
import mappy

from ont_fast5_api.fast5_interface import get_fast5_file

from pyguppyclient import GuppyBasecallerClient, yield_reads
from pyguppyclient.decode import ReadData

guppy_config = "/opt/ont/guppy/data/dna_r9.4.1_450bps_hac.cfg"

def yield_read_chunks(filename, start, length):
    with get_fast5_file(filename, 'r') as f5_fh:
        for read in f5_fh.get_reads():
            raw = read.handle[read.raw_dataset_name][start:start+length]
            if len(raw) < length: continue
            channel_info = read.handle[read.global_key + 'channel_id'].attrs
            scaling = channel_info['range'] / channel_info['digitisation']
            offset = int(channel_info['offset'])
            yield ReadData(raw, read.read_id, scaling=scaling, offset=offset)

################################################################################

def main(args):

    # initialize guppy and mappy
    virus_ref = mappy.Aligner(
            fn_idx_in = args.virus_dir+"/reference.fasta",
            preset = "map-ont",
            best_n = 1
    )
    with GuppyBasecallerClient(guppy_config, port=1234) as client:

        # perform analyses for each read length
        for length in [int(l) for l in args.chunk_lengths.split(",")]:
            print(f"Chunk length: {length}")

            # basecall and align all virus reads 
            virus_reads, virus_hits = 0, 0
            for fast5_fn in glob(args.virus_dir + "/fast5/*.fast5"):
                for read in yield_read_chunks(fast5_fn, args.trim_start, length):
                    virus_reads += 1
                    called = client.basecall(read)
                    for hit in virus_ref.map(called.seq):
                        virus_hits += 1

                    if virus_reads >= args.max_virus_reads:
                        break
                if virus_reads >= args.max_virus_reads:
                    break
            print(f"\tVirus mapped-unmapped: {virus_hits}-{args.max_virus_reads-virus_hits}")

            # basecall and align all other reads 
            other_reads, other_hits = 0, 0
            for fast5_fn in glob(args.other_dir + "/fast5/*.fast5"):
                for read in yield_read_chunks(fast5_fn, args.trim_start, length):
                    other_reads += 1
                    called = client.basecall(read)
                    for hit in virus_ref.map(called.seq):
                        other_hits += 1

                    if other_reads >= args.max_other_reads:
                        break
                if other_reads >= args.max_other_reads:
                    break

            print(f"\tOther mapped-unmapped: {other_hits}-{args.max_other_reads-other_hits}")



################################################################################

def parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--virus_dir", default="/x/squiggalign_data/lambda")
    parser.add_argument("--other_dir", default="/x/squiggalign_data/human")

    parser.add_argument("--trim_start", type=int, default=1000)
    parser.add_argument("--chunk_lengths", 
            default="1000,2000,3000,4000,5000,6000,7000")
    parser.add_argument("--max_virus_reads", type=int, default=10)
    parser.add_argument("--max_other_reads", type=int, default=10)

    return parser

################################################################################

if __name__ == "__main__":
    parser = parser()
    args = parser.parse_args()
    main(args)
