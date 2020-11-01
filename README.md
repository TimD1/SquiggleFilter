# SquiggAlign
Rapid long-read squiggle alignment to a short viral reference genome.

#Datasets:
covid: /z/scratch1/hariss/covid/  
human: /y/hariss/FAST5/50-50/c/h  
zymo: /y/hariss/FAST5/50-50/c/z  

Normalize using RawMap (from public repo with modified RawMap.cpp file) followed by dtw:

1. find {datasetpath} -type f > input
2. Clone RawMap form https://github.com/harisankarsadasivan/RawMap. Modify the top file with the top file RawMap.cpp with the one in SquiggAlign repo. 
./RawMap train input {empty dummy file name} > input_log
Open input_log and trim beginning and end.
3. Change <input_log> in the notebook script.
4. Run notebook on python
