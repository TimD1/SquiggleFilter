onbreak {quit -force}
onerror {quit -force}

asim -t 1ps +access +r +m+div_gen_0 -L xbip_utils_v3_0_10 -L axi_utils_v2_0_6 -L xbip_pipe_v3_0_6 -L xbip_dsp48_wrapper_v3_0_4 -L xbip_dsp48_addsub_v3_0_6 -L xbip_bram18k_v3_0_6 -L mult_gen_v12_0_15 -L floating_point_v7_0_16 -L xbip_dsp48_mult_v3_0_6 -L xbip_dsp48_multadd_v3_0_6 -L div_gen_v5_1_15 -L xil_defaultlib -L secureip -O5 xil_defaultlib.div_gen_0

do {wave.do}

view wave
view structure

do {div_gen_0.udo}

run -all

endsim

quit -force
