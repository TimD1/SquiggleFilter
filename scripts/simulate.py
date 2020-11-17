
#########################
###### PARAMETERS #######
#########################

# sample
avg_virus_read_len = 100_000.0                                  # signals
avg_other_read_len = 100_000.0                                  # signals
avg_read_trim = 1_000.0                                         # signals
ratio = 100.0                                                   # none
# coverage bias

# run-until information
genome_size = 30_000.0                                          # bases
target_coverage = 10.0                                          # none

# read-until strategy
ru_lengths = [3_000.0]                                          # signals
ru_virus_acc= [0.9]                                             # none
ru_other_acc= [0.9]                                             # none
decision_latency = 0.010                                        # seconds

# flow cell / pore chemistry
avg_capture_time = 1.0                                          # seconds
avg_fwd_rate = 400.0                                            # bases/second
avg_rev_rate = 100_000.0                                        # bases/second
minknow_reversal_latency = 0.070                                # seconds
sampling_rate = 4_000.0                                         # signals/second

# device
channels = 512.0                                                # none
prop_channels_blocked = 0.3                                     # none

#########################
###### CALCULATIONS #####
#########################

################################################################################

def basic_runtime(ratio):
    unblocked_channels = (1 - prop_channels_blocked) * channels
    max_throughput = unblocked_channels * avg_fwd_rate
    prop_virus = 1.0 / (1.0 + ratio)
    prop_other = 1 - prop_virus
    virus_time = (avg_capture_time + avg_virus_read_len/avg_fwd_rate)*prop_virus
    other_time = (avg_capture_time + avg_other_read_len/avg_fwd_rate)*prop_other
    all_time = virus_time + other_time
    useful_time = prop_virus * (avg_virus_read_len-avg_read_trim)/avg_fwd_rate
    prop_useful_time = useful_time / all_time
    useful_throughput = max_throughput * prop_useful_time
    run_until_duration = genome_size * target_coverage / useful_throughput
    return run_until_duration

################################################################################

def single_read_until_runtime(ratio):

    unblocked_channels = (1.0 - prop_channels_blocked) * channels
    max_throughput = unblocked_channels * avg_fwd_rate
    prop_virus = 1.0 / (1.0 + ratio)
    prop_other = 1 - prop_virus

    bases_sequenced = ru_lengths[0] + \
            (minknow_reversal_latency + decision_latency) * \
            avg_fwd_rate

    reverse_latency = decision_latency + \
            minknow_reversal_latency + \
            bases_sequenced / avg_rev_rate

    kept_viruses_time = ru_virus_acc[0] * prop_virus * \
            (avg_capture_time + avg_virus_read_len/avg_fwd_rate)
    tossed_viruses_time = (1-ru_virus_acc[0]) * prop_virus * \
            (avg_capture_time + bases_sequenced/avg_fwd_rate + reverse_latency)
    kept_others_time = (1-ru_other_acc[0]) * prop_other * \
            (avg_capture_time + avg_other_read_len/avg_fwd_rate)
    tossed_others_time = (ru_other_acc[0]) * prop_other * \
            (avg_capture_time + bases_sequenced/avg_fwd_rate + reverse_latency)

    all_time = kept_viruses_time + tossed_viruses_time + \
            kept_others_time + tossed_others_time
    useful_time = prop_virus * (avg_virus_read_len-avg_read_trim)/avg_fwd_rate
    prop_useful_time = useful_time / all_time

    useful_throughput = max_throughput * prop_useful_time
    run_until_duration = genome_size * target_coverage / useful_throughput
    return run_until_duration

for ratio in [1, 10, 100, 1000]:
    print(f"basic:\t{basic_runtime(ratio)}\tread-until:\t{single_read_until_runtime(ratio)}")
