import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import matplotlib
matplotlib.rcParams.update({'font.size': 14})

#########################
###### PARAMETERS #######
#########################

# sample
avg_virus_read_len = 10_000.0                                  # samples
avg_other_read_len = 10_000.0                                  # samples
avg_read_trim = 1_000.0                                         # samples
ratio = 100.0                                                   # none
# coverage bias

# run-until information
target_coverage = 30.0                                          # none

# read-until strategy
ru_lengths = [3_000.0]                                          # samples
ru_virus_acc= [0.9]                                             # none
ru_other_acc= [0.9]                                             # none

# flow cell / pore chemistry
avg_capture_time = 1.0                                          # seconds
avg_fwd_rate = 400.0                                            # bases/second
avg_rev_rate = 100_000.0                                        # bases/second
minknow_reversal_latency = 0.070                                # seconds
sampling_rate = 4_000.0                                         # samples/second

# device
channels = 512.0                                                # none
prop_channels_blocked = 0.0                                     # none

#########################
###### CALCULATIONS #####
#########################

################################################################################

# modify decision latency and basecalling throughput

basetype = "rtDNA"
species_name = "covid"
species_plotname = "COVID"

# basetype = "DNA"
# species_name = "lambda"
# species_plotname = "Lambda Phage"

if species_name == "covid":
    avg_virus_read_len = 10_000.0                                  # samples
    avg_other_read_len = 10_000.0                                  # samples
    genome_size = 30_000.0                                          # bases
else:
    avg_virus_read_len = 50_000.0                                  # samples
    avg_other_read_len = 50_000.0                                  # samples
    genome_size = 50_000.0                                          # bases

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

# def multi_read_until_runtime(ratio, ru_lengths, ru_virus_acc, ru_other_acc):

#     unblocked_channels = (1.0 - prop_channels_blocked) * channels
#     max_throughput = unblocked_channels * avg_fwd_rate

#     bases_sequenced = ru_lengths[0] + \
#             (minknow_reversal_latency + decision_latency) * \
#             avg_fwd_rate

#     reverse_latency = decision_latency + \
#             minknow_reversal_latency + \
#             bases_sequenced / avg_rev_rate

#     prop_virus = 1.0 / (1.0 + ratio)
#     prop_other = 1 - prop_virus
#     useful_viruses_time = np.prod(ru_virus_acc) * prop_virus * \
#             (avg_virus_read_len-avg_read_trim)/avg_fwd_rate
#     kept_viruses_time = np.prod(ru_virus_acc) * prop_virus * \
#             (avg_capture_time + avg_virus_read_len/avg_fwd_rate)
#     kept_others_time = np.prod([1-x for x in ru_other_acc]) * prop_other * \
#             (avg_capture_time + avg_other_read_len/avg_fwd_rate)
#     tossed_viruses_time = 0
#     tossed_others_time = 0
#     for i in range(len(ru_virus_acc)):
#         tossed_viruses_time += (1 - ru_virus_acc[i]) * prop_virus * \
#                 (avg_capture_time + bases_sequenced/avg_fwd_rate + reverse_latency)
#         tossed_others_time += ru_other_acc[i] * prop_other * \
#                 (avg_capture_time + bases_sequenced/avg_fwd_rate + reverse_latency)
#         prop_virus = prop_virus * ru_virus_acc[i]
#         prop_other = prop_other * (1-ru_other_acc[i])

#     all_time = kept_viruses_time + tossed_viruses_time + \
#             kept_others_time + tossed_others_time
#     prop_useful_time = useful_viruses_time / all_time

#     useful_throughput = max_throughput * prop_useful_time
#     run_until_duration = genome_size * target_coverage / (useful_throughput + 0.00001)
#     return run_until_duration

def single_read_until_runtime(ratio, ru_lengths, ru_virus_acc, ru_other_acc):

    unblocked_channels = (1.0 - prop_channels_blocked) * channels
    seq_throughput = unblocked_channels * avg_fwd_rate
    prop_virus = 1.0 / (1.0 + ratio)
    prop_other = 1 - prop_virus

    # get proportion of pores which can do read-until
    prop_ru = min(1.0, basecall_throughput / seq_throughput)
    prop_simple = 1.0 - prop_ru

    # SIMPLE 
    simple_virus_time = (avg_capture_time + avg_virus_read_len/avg_fwd_rate)*prop_virus
    simple_other_time = (avg_capture_time + avg_other_read_len/avg_fwd_rate)*prop_other
    simple_useful_time = prop_virus * (avg_virus_read_len-avg_read_trim)/avg_fwd_rate
    simple_prop_useful_time = simple_useful_time / \
            (simple_virus_time + simple_other_time)

    # READ UNTIL
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
    ru_time = kept_viruses_time + tossed_viruses_time + \
            kept_others_time + tossed_others_time
    ru_prop_useful_time = useful_viruses_time / ru_time

    prop_useful_time = prop_ru * ru_prop_useful_time + \
            prop_simple * simple_prop_useful_time
    useful_throughput = seq_throughput * prop_useful_time
    run_until_duration = genome_size * target_coverage / (useful_throughput + 0.00001)
    return run_until_duration

def load_scores(score_dir, length):
    ba_virus = np.load(f"{score_dir}/{length}sigs_ba_virus_scores.npy")
    ba_other = np.load(f"{score_dir}/{length}sigs_ba_other_scores.npy")
    dtw_virus = np.load(f"{score_dir}/{length}sigs_dtw_virus_scores.npy")
    dtw_other = np.load(f"{score_dir}/{length}sigs_dtw_other_scores.npy")
    return ba_virus, ba_other, dtw_virus, dtw_other

# lengths = list(range(1000, min(10001, int(avg_virus_read_len-avg_read_trim+1)), 1000))
lengths = [1000, 2000, 3000, 8000]
thresholds = { 1000: 3900, 2000: 7750, 3000: 12000, 4000: 16500, 5000: 20000, \
        6000: 24000, 7000: 29500, 8000: 33000, 9000: 37000, 10000: 40000 }

fig1, ax1 = plt.subplots()                                                     
fig2, ax2 = plt.subplots()                                                     
fig3, ax3 = plt.subplots()                                                     
fig4, ax4 = plt.subplots()                                                     
chosen_runtimes = []
ax2.plot(0, 1, color='k', marker='*', markersize=15, linestyle='None')
ax2.plot([0,1], [0,1], color='k', marker='None', linestyle=':')
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
    decision_latency = 0.149                                        # seconds
    basecall_throughput = 95700.0 # approx Xavier read-until basecalling throughput
    ba_virus_discard_rate, ba_other_discard_rate = [], []                        
    dtw_virus_discard_rate, dtw_other_discard_rate = [], []                      
    for t in ba_thresholds:                                                      
        ba_virus_discard_rate.append(sum(ba_virus < t) / len(ba_virus))          
        ba_other_discard_rate.append(sum(ba_other < t) / len(ba_other))          
        ba_runtimes.append(
                single_read_until_runtime(ratio, [length+avg_read_trim], 
                    [1-ba_virus_discard_rate[-1]], [ba_other_discard_rate[-1]])
                )

    first_above_threshold = True
    decision_latency = 0.0003                                        # seconds
    decision_latency = 0.216                                        # seconds
    basecall_throughput = 100000000
    for t in dtw_thresholds:                                                     
        dtw_virus_discard_rate.append(sum(dtw_virus > t) / len(dtw_virus))            
        dtw_other_discard_rate.append(sum(dtw_other > t) / len(dtw_other))            
        dtw_runtime = single_read_until_runtime(ratio, [length+avg_read_trim], 
                    [1-dtw_virus_discard_rate[-1]], [dtw_other_discard_rate[-1]])
        dtw_runtimes.append(dtw_runtime)
        if t > thresholds[length] and first_above_threshold:
            first_above_threshold = False
            chosen_runtimes.append(dtw_runtime)
            print(f'Length: {length}\tDTW: {dtw_runtime}')

    # plot basecall-align discard rate                                           
    ax1.plot(ba_virus_discard_rate, ba_other_discard_rate, marker='o', alpha=0.5) 
    ax1.set_xlabel(f'{species_plotname} Discard Rate')                          
    ax1.set_ylabel(f'Human Discard Rate')                          
    ax1.set_title(f'Guppy-lite + Minimap2 Accuracy')                   
    ax1.set_xlim((-0.1, 1.1))                                                     
    ax1.set_ylim((-0.1, 1.1))                                                     
    ax1.legend([str(x)+' samples' for x in lengths], loc="lower right")

######## 

    # plot runtimes
    ax3.plot(ba_thresholds, ba_runtimes, marker='o', alpha=0.5) 
    ax3.set_xlabel(f'Mapping Quality Threshold')                          
    ax3.set_ylabel(f'Sequencing Runtime (seconds)')                          
    ax3.set_ylim((-0.1, 1000))                                                     
    # plot runtimes
    ax4.plot(dtw_thresholds, dtw_runtimes, marker='o', alpha=0.5) 
    ax4.set_xlabel(f'Alignment Score Threshold')                          
    ax4.set_ylabel(f'Sequencing Runtime (seconds)')                          
    ax4.set_ylim((-0.1, 750))                                                     
    ax4.set_xlim((0, 80000))                                                     
    ax4.set_xticks([0, 80000])

########
    lengths2 = [1000, 2000, 3000, 8000]
    if length in lengths2:
        # plot dtw-align discard rate                                                
        ax2.plot(dtw_virus_discard_rate, dtw_other_discard_rate, marker='o', alpha=0.5)
        ax2.set_xlabel(f'{species_plotname} Discard Rate')                          
        ax2.set_ylabel(f'Human Discard Rate')                          
        ax2.set_xlim((-0.1, 1.1))                                                     
        ax2.set_ylim((-0.1, 1.1))                                                     
ba_virus, ba_other, dtw_virus, dtw_other = \
        load_scores(f"../data/scores/{basetype}/{species_name}0_human0", 2000)
ba_thresholds = np.linspace(                                                 
        min(np.min(ba_virus), np.min(ba_other))-1,                           
        max(np.max(ba_virus), np.max(ba_other))+1, num=100)                  
ba_virus_discard_rate, ba_other_discard_rate = [], []                        
for t in ba_thresholds:                                                      
    ba_virus_discard_rate.append(sum(ba_virus < t) / len(ba_virus))          
    ba_other_discard_rate.append(sum(ba_other < t) / len(ba_other))          
ax2.plot(ba_virus_discard_rate, ba_other_discard_rate, marker='o', alpha=0.5) 
ax2.legend(["ideal", "random"] + \
        [f"SquiggleFilter {x} samples" for x in lengths2] + \
        ["Guppy-lite 2000 samples"], loc="lower right")
########


fig1.savefig(f'../img/{basetype}_ba_curve.png')                       
fig2.savefig(f'../img/{basetype}_dtw_curve.png', dpi=300)                     
print("Basic:", basic_runtime(ratio))
ax3.axhline(y=basic_runtime(ratio), color='k', linestyle='--')
ax3.legend([str(x)+' sample Read Until' for x in lengths] + ['no Read Until'], loc="upper right")
fig3.tight_layout()
fig4.tight_layout()
fig3.savefig(f'../img/{basetype}_ba_ru_time.png')                     
# ax4.plot([thresholds[length] for length in lengths], chosen_runtimes, color='k', marker='x', linestyle='None')
ax4.plot([thresholds[2000]], chosen_runtimes[1], color='k', marker='*', markersize=15, linestyle='None')
ax4.axhline(y=basic_runtime(ratio), color='k', linestyle='--')
# ax4.legend([str(x)+' samples' for x in lengths] + ['candidate thresholds', 'selected threshold', 'no read-until'])
ax4.legend([str(x)+' sample Read Until' for x in lengths] + ['Selected Threshold', 'No Read Until'], loc="lower right")
    # ax4.plot([thresholds[2000]], chosen_runtimes, color='k', marker='*', markersize=15, linestyle='None')
    # ax4.axhline(y=basic_runtime(ratio), color='k', linestyle='--')
    # ax4.legend([str(x)+' samples' for x in lengths] + ['selected threshold', 'no read-until'])
fig4.savefig(f'../img/{basetype}_dtw_ru_time.png', dpi=300)                     

# avg_virus_read_len = 50_000.0                                  # samples
# avg_other_read_len = 50_000.0                                  # samples

# fig5, ax5 = plt.subplots()                                                     
# for avg_capture_time in [0, 1]:
#     basic_runtimes = []
#     ba_ratio_runtimes = []
#     dtw_ratio_runtimes = []
#     ratios = list(range(10,1000,20))
#     length = 2000
#     for ratio in ratios:
#         # plot basic runtime 
#         basic_runtimes.append(basic_runtime(ratio))
#         ba_virus, ba_other, dtw_virus, dtw_other = \
#             load_scores(f"../data/scores/{basetype}/{species_name}0_human0", length)

#         # plot benefit with read-until
#         ba_ru_virus_acc = sum(ba_virus > 0) / len(ba_virus)
#         ba_ru_other_acc = 1 - (sum(ba_other > 0) / len(ba_other))
#         ba_ratio_runtimes.append(single_read_until_runtime( \
#                 ratio, [length + avg_read_trim], [ba_ru_virus_acc], [ba_ru_other_acc]))
#         dtw_ru_virus_acc = sum(dtw_virus < thresholds[length]) / len(dtw_virus)
#         dtw_ru_other_acc = 1 - (sum(dtw_other < thresholds[length]) / len(dtw_other))
#         dtw_ratio_runtimes.append(single_read_until_runtime( \
#                 ratio, [length + avg_read_trim], [dtw_ru_virus_acc], [dtw_ru_other_acc]))

#     if avg_capture_time: marker = 'o'
#     else: marker = '.'
#     ax5.plot(ratios, ba_ratio_runtimes, color='C1', marker=marker, alpha=0.5) 
#     ax5.plot(ratios, dtw_ratio_runtimes, color='C2', marker=marker, alpha=0.5) 
#     ax5.plot(ratios, basic_runtimes, color='k', linestyle='--' )
# ax5.set_xlabel(f'Host to Bug Ratio')                          
# ax5.set_ylabel(f'Read Until Runtime (seconds)')                          
# ax5.set_title(f'Read Until Runtimes')                   
# lines = [Line2D([0],[0], color='C1', marker='o'),
#         Line2D([0],[0], color='C2', marker='o'),
#         Line2D([0],[0], color='k', marker='.'),
#         Line2D([0],[0], color='k', linestyle='--')]
# labels = [f'Guppy-lite: {length} samples', f'SquiggleFilter: {length} samples', 'zero capture time', 'no read-until']
# ax5.legend(lines, labels)
# ax5.set_ylim((-0.1, 2000))                                                     
# fig5.savefig(f'../img/ratio_ru_time.png')                     

# fig6, ax6 = plt.subplots()                                                     
# ratio = 100
# for avg_capture_time in [0, 1]:
#     basic_runtimes = []
#     ba_readlen_runtimes = []
#     dtw_readlen_runtimes = []
#     read_lengths = list(range(10000,100000,2000))
#     length = 2000
#     for avg_virus_read_len, avg_other_read_len in zip(read_lengths, read_lengths):
#         # plot basic runtime 
#         basic_runtimes.append(basic_runtime(ratio))
#         ba_virus, ba_other, dtw_virus, dtw_other = \
#             load_scores(f"../data/scores/{basetype}/{species_name}0_human0", length)

#         # plot benefit with read-until
#         ba_ru_virus_acc = sum(ba_virus > 0) / len(ba_virus)
#         ba_ru_other_acc = 1 - (sum(ba_other > 0) / len(ba_other))
#         ba_readlen_runtimes.append(single_read_until_runtime( \
#                 ratio, [length + avg_read_trim], [ba_ru_virus_acc], [ba_ru_other_acc]))
#         dtw_ru_virus_acc = sum(dtw_virus < thresholds[length]) / len(dtw_virus)
#         dtw_ru_other_acc = 1 - (sum(dtw_other < thresholds[length]) / len(dtw_other))
#         dtw_readlen_runtimes.append(single_read_until_runtime( \
#                 ratio, [length + avg_read_trim], [dtw_ru_virus_acc], [dtw_ru_other_acc]))

#     if avg_capture_time: marker = 'o'
#     else: marker = '.'
#     ax6.plot(read_lengths, ba_readlen_runtimes, color='C1', marker=marker, alpha=0.5) 
#     ax6.plot(read_lengths, dtw_readlen_runtimes, color='C2', marker=marker, alpha=0.5) 
# ax6.plot(read_lengths, basic_runtimes, color='k', linestyle='--' )
# ax6.set_xlabel(f'Average Read Length (samples)')                          
# ax6.set_ylabel(f'Read Until Runtime (seconds)')                          
# ax6.set_title(f'Read Until Runtimes')                   
# lines = [Line2D([0],[0], color='C1', marker='o'),
#         Line2D([0],[0], color='C2', marker='o'),
#         Line2D([0],[0], color='k', marker='.'),
#         Line2D([0],[0], color='k', linestyle='--')]
# labels = [f'Guppy-lite: {length} samples', f'SquiggleFilter: {length} samples', 'zero capture time', 'no read-until']
# ax6.legend(lines, labels)
# ax6.set_ylim((-0.1, 800))                                                     
# fig6.savefig(f'../img/readlen_ru_time.png')                     
