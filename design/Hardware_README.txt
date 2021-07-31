Vivado 2019 Installation:
https://www.xilinx.com/support/documentation-navigation/design-hubs/2019-1/dh0013-vivado-installation-and-licensing-hub.html
If vivado does not open/crashes, please check Xilinx SDK requirements (I ran it on my Quadcore i-5 8th gen with 8G memory):
https://www.xilinx.com/html_docs/xilinx2019_1/SDK_Doc/xsct/intro/xsct_system_requirements.html

1.======Loading the environment:=========
1.1Uncompress design/verilog.tar. The project folder is compressed because of git's size limit of 100MB. User may only uncompress this, install Vivado
and run the project.

2.Open a project on Vivado under the File tabe and load design/verilog/verilog_v2.xpr from the uncompressed folder.

3.============= Settings:==================

3.1 Set the reference filename on the "reference_filename" and local query filepath on the "query_filename" in testbench_top.sv. Make sure to do this in all 3 places it appears in the file.
3.2 Set simulation runtime under tools->settings to 18ms.

4.=================Defaults & description:================


-testbench_top.sv is the top file of the testbench simulation environment.
-warper_top.sv is the top file of the systolic array.
-normalizer_top.sv is the top file of the normalizer.
-constants.h: the reference length can be controlled with REF_MAX_LEN and QUERY_LEN can be controlled with QUERY_LEN.
-This project does use integer adder,subtractor,divider and accumulator IPs from Xilinx. They are linked to the project environment.
-Smaller QUERY size of 100 vs original SARS-CoV-2 reference is used for this artifact for sensible simulation times and resource usage. 
However, if one may wish to do so,one may vary QUERY_LEN under constants.vh from 1-500 on the datasets in design/sv_sim_datasets.
-The BRAM and DRAM are not connected and query and reference sequences are loaded from text file.

5.================== The testbench===================

The testbench loads test vectors from a subset of our public datasets in design/sv_sim_datasets. Make sure to update your local path in testench 
before starting simulation. It compares the output of the design in "result" when "done" is set high to our expectation: 1 for virus and 1 for human.

6.============= Behavioral simulation using the testbench:===============

Go to the flow navigator on the left hand side tab and press "run simulation" to start the simulation. Watch the test case number and PASSED/FAILED displays on the tcl console. The behavioral simulation may also be inspected by looking at the waveform. We observe & expect all 18 testcases to pass.