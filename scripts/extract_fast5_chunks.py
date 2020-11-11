import h5py
from glob import glob
import os
import numpy as np

species = "lambda"
reads = 100
start = 1000
lengths = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
input_dir = "/x/squiggalign_data/" + species + "/fast5"
main_output_dir = "/x/squiggalign_data/accuracy"

# create an output fast5 with signals of all same length
input_fast5s = glob(input_dir + "/*.fast5")
for length in lengths:
    output_dir = f"{main_output_dir}/{reads}{species}/{length}signals"
    output_fast5_fn = output_dir + "/reads.fast5"
    os.makedirs(output_dir, exist_ok=True)
    output_fast5 = h5py.File(output_fast5_fn, 'w')

    # take reads from input files
    read_count = 0
    for input_fast5_fn in input_fast5s:
        input_fast5 = h5py.File(input_fast5_fn, 'r')

        for read in input_fast5:

            # stop early if we've found enough reads
            if read_count >= reads: 
                break

            # filter for long enough reads
            read_signal_length = len(input_fast5[read]['Raw']['Signal'][:])
            if read_signal_length > start + max(lengths):

                # add trimmed reads to output file
                output_fast5.create_group(read)
                input_fast5[read]['Raw'].copy(input_fast5[read]['Raw'], output_fast5[read])
                input_fast5[read]['channel_id'].copy(input_fast5[read]['channel_id'], output_fast5[read])
                input_fast5[read]['tracking_id'].copy(input_fast5[read]['tracking_id'], output_fast5[read])
                input_fast5[read]['context_tags'].copy(input_fast5[read]['context_tags'], output_fast5[read])

                # https://stackoverflow.com/questions/38267076/how-to-write-a-dataset-of-null-terminated-fixed-length-strings-with-h5py
                be_dt = h5py.h5t.C_S1.copy()
                be_dt.set_size(len("0")+1)
                output_fast5[read]['context_tags'].attrs.create('barcoding_enabled', 
                        "0", dtype=h5py.Datatype(be_dt))

                cv_dt = h5py.h5t.C_S1.copy()
                cv_dt.set_size(len("1.0.1")+1)
                output_fast5[read]['tracking_id'].attrs.create('configuration_version',
                        "1.0.1", dtype=h5py.Datatype(cv_dt))

                pc_dt = h5py.h5t.C_S1.copy()
                pc_dt.set_size(len(output_fast5[read]['context_tags'].attrs['flow_cell_product_code'])+1)
                output_fast5[read]['tracking_id'].attrs.create('flow_cell_product_code',  \
                        output_fast5[read]['context_tags'].attrs['flow_cell_product_code'],
                        dtype=h5py.Datatype(pc_dt))
                del output_fast5[read]['context_tags'].attrs['flow_cell_product_code']

                pt_dt = h5py.h5t.C_S1.copy()
                pt_dt.set_size(len(input_fast5[read].attrs['pore_type'])+1)
                output_fast5[read].attrs.create('pore_type', input_fast5[read].attrs['pore_type'],
                        dtype=h5py.Datatype(pt_dt))

                ri_dt = h5py.h5t.C_S1.copy()
                ri_dt.set_size(len(input_fast5[read].attrs['run_id'])+1)
                output_fast5[read].attrs.create('run_id', input_fast5[read].attrs['run_id'],
                        dtype=h5py.Datatype(ri_dt))

                end_reason = h5py.enum_dtype({"unknown":0, "partial":1, "mux_change":2, "unblock_mux_change":3,"signal_positive":4,"signal_negative":5}, basetype=np.ubyte)
                output_fast5[read]['Raw'].attrs.create("end_reason", 4, dtype=end_reason)

                signal_dataset = output_fast5[read]['Raw']['Signal']
                signal_dataset.resize((length,))
                signal_dataset[:] = input_fast5[read]['Raw']['Signal'][start:start+length]
                read_count += 1

            else:
                continue

        if read_count >= reads:
            break
