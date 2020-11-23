import matplotlib.pyplot as plt
import numpy as np

#########################
###### PARAMETERS #######
#########################

# sample
avg_virus_read_len = 10_000.0                                  # signals
avg_other_read_len = 10_000.0                                  # signals
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
decision_latency = 0.100                                        # seconds

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

basetype = "rtDNA"
species_name = "covid"
species_plotname = "COVID"

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

def single_read_until_runtime(ratio, ru_lengths, ru_virus_acc, ru_other_acc):

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

    useful_viruses_time = ru_virus_acc[0] * prop_virus * \
            (avg_virus_read_len-avg_read_trim)/avg_fwd_rate
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
    prop_useful_time = useful_viruses_time / all_time

    useful_throughput = max_throughput * prop_useful_time
    run_until_duration = genome_size * target_coverage / (useful_throughput + 0.00001)
    return run_until_duration

def load_scores(score_dir, length):
    ba_virus = np.load(f"{score_dir}/{length}sigs_ba_virus_scores.npy")
    ba_other = np.load(f"{score_dir}/{length}sigs_ba_other_scores.npy")
    dtw_virus = np.load(f"{score_dir}/{length}sigs_dtw_virus_scores.npy")
    dtw_other = np.load(f"{score_dir}/{length}sigs_dtw_other_scores.npy")
    return ba_virus, ba_other, dtw_virus, dtw_other

fig1, ax1 = plt.subplots()                                                     
fig2, ax2 = plt.subplots()                                                     
fig3, ax3 = plt.subplots()                                                     
fig4, ax4 = plt.subplots()                                                     
lengths = list(range(1000, 10001, 1000))
thresholds = { 1000: 3900, 2000: 7750, 3000: 12000, 4000: 16500, 5000: 20000, \
        6000: 24000, 7000: 29500, 8000: 33000, 9000: 37000, 10000: 40000 }
chosen_runtimes = []
for length in lengths:
    ba_runtimes = []
    dtw_runtimes = []
    ba_virus, ba_other, dtw_virus, dtw_other = \
            load_scores(f"../data/scores/{basetype}/{species_name}0_human0", length)

    # create thresholds for plotting                                             
    ba_thresholds = np.linspace(                                                 
            min(np.min(ba_virus), np.min(ba_other))-1,                           
            max(np.max(ba_virus), np.max(ba_other))+1, num=100)                  
    dtw_thresholds = np.linspace(                                                
            min(np.min(dtw_virus), np.min(dtw_other))-1,                         
            max(np.max(dtw_virus), np.max(dtw_other))+1, num=100)                

    # calculate discard rate of each                                             
    ba_virus_discard_rate, ba_other_discard_rate = [], []                        
    dtw_virus_discard_rate, dtw_other_discard_rate = [], []                      
    for t in ba_thresholds:                                                      
        ba_virus_discard_rate.append(sum(ba_virus < t) / len(ba_virus))          
        ba_other_discard_rate.append(sum(ba_other < t) / len(ba_other))          
        ba_runtimes.append(
                single_read_until_runtime(ratio, [length], 
                    [1-ba_virus_discard_rate[-1]], [ba_other_discard_rate[-1]])
                )

    first_above_threshold = True
    for t in dtw_thresholds:                                                     
        dtw_virus_discard_rate.append(sum(dtw_virus > t) / len(dtw_virus))            
        dtw_other_discard_rate.append(sum(dtw_other > t) / len(dtw_other))            
        dtw_runtime = single_read_until_runtime(ratio, [length], 
                    [1-dtw_virus_discard_rate[-1]], [dtw_other_discard_rate[-1]])
        dtw_runtimes.append(dtw_runtime)
        if t > thresholds[length] and first_above_threshold:
            first_above_threshold = False
            chosen_runtimes.append(dtw_runtime)

    # plot basecall-align discard rate                                           
    ax1.plot(ba_virus_discard_rate, ba_other_discard_rate, marker='o', alpha=0.5) 
    ax1.set_xlabel(f'{species_plotname} Discard Rate')                          
    ax1.set_ylabel(f'Human Discard Rate')                          
    ax1.set_title(f'High-Acc Guppy + Minimap2 Accuracy')                   
    ax1.set_xlim((-0.1, 1.1))                                                     
    ax1.set_ylim((-0.1, 1.1))                                                     
    ax1.legend([str(x)+' signals' for x in lengths])

    # plot dtw-align discard rate                                                
    ax2.plot(dtw_virus_discard_rate, dtw_other_discard_rate, marker='o', alpha=0.5)
    ax2.set_xlabel(f'{species_plotname} Discard Rate')                          
    ax2.set_ylabel(f'Human Discard Rate')                          
    ax2.set_title(f'SquiggleFilter Accuracy')                        
    ax2.set_xlim((-0.1, 1.1))                                                     
    ax2.set_ylim((-0.1, 1.1))                                                     
    ax2.legend([str(x)+' signals' for x in lengths])

    # plot runtimes
    ax3.plot(ba_thresholds, ba_runtimes, marker='o', alpha=0.5) 
    ax3.set_xlabel(f'Threshold Values')                          
    ax3.set_ylabel(f'Read-Until Runtimes')                          
    ax3.set_title(f'High-Acc Guppy + Minimap2 Read-Until Runtimes')                   
    ax3.set_ylim((-0.1, 300))                                                     
    # plot runtimes
    ax4.plot(dtw_thresholds, dtw_runtimes, marker='o', alpha=0.5) 
    ax4.set_xlabel(f'Threshold Values')                          
    ax4.set_ylabel(f'Read-Until Runtimes')                          
    ax4.set_title(f'SquiggleFilter Read-Until Runtimes')                   
    ax4.set_ylim((-0.1, 300))                                                     

fig1.savefig(f'../img/{basetype}_ba_curve.png')                       
fig2.savefig(f'../img/{basetype}_dtw_curve.png')                     
ax3.axhline(y=basic_runtime(ratio), color='k', linestyle='--')
ax3.legend([str(x)+' signals' for x in lengths] + ['no read-until'])
fig3.savefig(f'../img/{basetype}_ba_ru_time.png')                     
ax4.plot([thresholds[length] for length in lengths], chosen_runtimes, color='k', marker='x', linestyle='None')
ax4.axhline(y=basic_runtime(ratio), color='k', linestyle='--')
ax4.legend([str(x)+' signals' for x in lengths] + ['selected', 'no read-until'])
fig4.savefig(f'../img/{basetype}_dtw_ru_time.png')                     


