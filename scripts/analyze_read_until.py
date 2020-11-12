from glob import glob
import argparse
import mappy

from ont_fast5_api.fast5_interface import get_fast5_file

import pyguppyclient
from pyguppyclient.decode import ReadData

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

def init(args):

    # parse input lengths and thresholds
    lengths = [int(l) for l in args.chunk_lengths.split(",")]
    thresholds = [int(t) for t in args.chunk_thresholds.split(",")]

    return lengths, thresholds

################################################################################

def basecall_align(folder, max_reads, length, args):

    # initialize mappy aligner
    aligner = mappy.Aligner(
            fn_idx_in = args.virus_dir+"/reference.fasta",
            preset = "map-ont",
            best_n = 1
    )

    # initialize guppy basecaller
    if args.nucleotide_type == "dna":
        guppy_config = f"/opt/ont/guppy/data/dna_r9.4.1_450bps_{args.model}.cfg"
    else:
        guppy_config = f"/opt/ont/guppy/data/rna_r9.4.1_70bps_{args.model}.cfg"

    reads, scores = 0, []
    with pyguppyclient.GuppyBasecallerClient(guppy_config, port=1234) as bc:
        for fast5_fn in glob(folder + "/fast5/*.fast5"):
            for read in yield_read_chunks(fast5_fn, args.trim_start, length):
                called = bc.basecall(read)
                try:
                    alignment = next(aligner.map(called.seq))
                    scores.append(alignment.mapq)
                except(StopIteration): # no alignment
                    scores.append(0)

                # quit early if we've hit our read limit
                if reads > max_reads: break
                reads += 1
            if reads > max_reads: break

        # return mapping scores
        return scores

################################################################################

def main(args):

    lengths, thresholds = init(args)

    for length in lengths:

        print(f"Chunk length: {length}")

        virus_scores = basecall_align( args.virus_dir, args.max_virus_reads, length, args)
        other_scores = basecall_align( args.other_dir, args.max_other_reads, 
                length, args)

        print(virus_scores)
        print(other_scores)

################################################################################

def parser():
    parser = argparse.ArgumentParser()

    # guppy parameters
    parser.add_argument("--nucleotide_type", default="dna")
    parser.add_argument("--model", default="hac")

    parser.add_argument("--virus_dir", default="/x/squiggalign_data/lambda")
    parser.add_argument("--other_dir", default="/x/squiggalign_data/human")

    parser.add_argument("--trim_start", type=int, default=1000)
    parser.add_argument("--chunk_lengths", 
            default="1000,2000,3000,4000,5000,6000,7000")
    parser.add_argument("--chunk_thresholds", 
            default="5500,11000,15000,19000,24000,29000,34000")
    parser.add_argument("--max_virus_reads", type=int, default=10)
    parser.add_argument("--max_other_reads", type=int, default=10)

    return parser

################################################################################

if __name__ == "__main__":
    parser = parser()
    args = parser.parse_args()
    main(args)
