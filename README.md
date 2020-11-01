# SquiggAlign
Rapid long-read squiggle alignment to a short viral reference genome.

#Datasets:
covid: /z/scratch1/hariss/covid/  
human: /y/hariss/FAST5/50-50/c/h  
zymo: /y/hariss/FAST5/50-50/c/z  

Normalize using RawMap followed by dtw:

1. find {datasetpath} -type f > input
2. Clone RawMap from https://github.com/harisankarsadasivan/RawMap. Modify the top file with the top file RawMap.cpp in SquiggAlign repo. 
./RawMap train input {empty dummy file name} > input_log
Open input_log and trim beginning and end.
Here, we only output the first 3000 squiggles following the first 1000 samples for every read in {input} file into input_log.
3. Change <input_log> in the notebook script to parse in input squiggles.
4. Run notebook on python
