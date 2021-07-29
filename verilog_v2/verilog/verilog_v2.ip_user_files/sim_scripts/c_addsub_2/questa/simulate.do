onbreak {quit -f}
onerror {quit -f}

vsim -t 1ps -lib xil_defaultlib c_addsub_2_opt

do {wave.do}

view wave
view structure
view signals

do {c_addsub_2.udo}

run -all

quit -force
