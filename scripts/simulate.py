
#########################
###### PARAMETERS #######
#########################

# sample
avg_virus_read_len = 100_000                                  # signals
avg_other_read_len = 100_000                                  # signals
avg_read_trim = 1_000                                         # signals
ratio = 100                                                   # none
# coverage bias

# run-until information
genome_size = 30_000                                          # bases
target_coverage = 10                                          # none

# read-until strategy
# due to adapter length and stall
ru_lengths = [3_000]                                          # signals
ru_virus_accuracies = [0.9]                                   # none
ru_other_accuracies = [0.9]                                   # none
decision_latency = 0.010                                      # seconds

# flow cell / pore chemistry
avg_capture_time = 1.0                                        # seconds
avg_fwd_rate = 400                                            # bases / second
avg_rev_rate = 100_000                                        # bases / second
minknow_reversal_latency = 0.070                              # seconds
sampling_rate = 4_000                                         # samples / second

# device
channels = 512                                                # MinION
prop_channels_blocked = 0.3                                      # none


#########################
###### CALCULATIONS #####
#########################

# average read length
avg_read_len = float(avg_virus_read_len + \
    ratio * avg_other_read_len) / (ratio + 1)                 # signals

def basic_runtime(ratio):
    unblocked_channels = (1 - prop_channels_blocked) * channels
    max_throughput = unblocked_channels * avg_fwd_rate            # bases / second
    time_unit = (avg_capture_time + avg_other_read_len/avg_fwd_rate)*ratio + \
            (avg_capture_time + avg_virus_read_len/avg_fwd_rate)  # seconds
    useful_time = (avg_virus_read_len-avg_read_trim)/avg_fwd_rate # seconds
    prop_useful_time = useful_time / time_unit                    # none
    useful_throughput = max_throughput * prop_useful_time         # bases / second
    read_until_duration = genome_size * target_coverage / \
            useful_throughput                                     # seconds
    return read_until_duration

for ratio in [1, 10, 100, 1000]:
    print(basic_runtime(ratio))
